import requests
import json
from typing import Dict, Any, Optional


def capture_variable_info(var_name: str, var_value: Any) -> Dict[str, Any]:
    """Capture information about a variable."""
    info = {
        "name": var_name,
        "type": None,
        "value": None,
        "shape": None,
        "min": None,
        "max": None
    }
    
    # Try NumPy
    try:
        import numpy as np
        if isinstance(var_value, np.ndarray):
            info["type"] = "numpy.ndarray"
            info["shape"] = list(var_value.shape)
            info["min"] = float(var_value.min())
            info["max"] = float(var_value.max())
            return info
    except:
        pass
    
    # Try PyTorch
    try:
        import torch
        if isinstance(var_value, torch.Tensor):
            info["type"] = "torch.Tensor"
            info["shape"] = list(var_value.shape)
            info["min"] = float(var_value.min().item())
            info["max"] = float(var_value.max().item())
            return info
    except:
        pass

    # Handle primitives
    if isinstance(var_value, (int, float)):
        info["type"] = "float" if isinstance(var_value, float) else "int"
        info["value"] = float(var_value)
        return info
    
    return info


def capture_variables() -> Dict[str, Dict[str, Any]]:
    """Capture all relevant variables from the caller's scope."""
    import inspect
    
    # Get the caller's global scope (2 frames back: capture_variables -> verify -> user code)
    frame = inspect.currentframe()
    try:
        caller_globals = frame.f_back.f_back.f_globals
    finally:
        del frame
    
    variables = {}
    excluded_names = {
        'In', 'Out', 'get_ipython', 'exit', 'quit', 
        'requests', 'json', 'np', 'torch', 'verify',
        '__name__', '__doc__', '__package__', '__loader__',
        '__spec__', '__annotations__', '__builtins__'
    }
    
    print("📊 Capturing variables...")
    
    for var_name, var_value in list(caller_globals.items()):
        # Skip private/excluded variables
        if var_name.startswith('_'):
            continue
        if var_name in excluded_names:
            continue
        
        # Skip modules
        if hasattr(var_value, '__file__'):
            continue
            
        # Skip callable objects (unless they have shape attribute)
        if callable(var_value) and not hasattr(var_value, 'shape'):
            continue
        
        try:
            info = capture_variable_info(var_name, var_value)
            if info["type"]:
                variables[var_name] = info
                print(f"   ✓ {var_name}")
        except:
            pass
    
    return variables


def verify(
    user_token: str,
    project_id: str,
    step: int,
    api_base_url: str = "https://www.crekai.com/api"
) -> None:
    """
    Verify your CrekAI assignment by capturing and submitting variables.
    
    Args:
        user_token: Your CrekAI user token
        project_id: Project identifier (e.g., "learn-numpy")
        step: Current step number
        api_base_url: API base URL (default: "https://www.crekai.com/api")
    
    Example:
        >>> from crekai_verifier import verify
        >>> import numpy as np
        >>> arr = np.array([1, 2, 3])
        >>> verify(
        ...     user_token="your_token_here",
        ...     project_id="learn-numpy",
        ...     step=1
        ... )
    """
    print("🔍 CrekAI Verification\n")
    
    # Capture variables
    variables = capture_variables()
    
    # Submit to API
    print("\n🚀 Submitting...\n")
    
    try:
        response = requests.post(
            f"{api_base_url}/track-execution",
            json={
                "token": user_token,
                "project_id": project_id,
                "step": step,
                "code": "executed",
                "output": {"variables": variables}
            },
            timeout=10
        )

        data = {}
        try:
            data = response.json()
        except:
            pass

        if response.status_code == 200:
            print("=" * 60)
            print("✅ SUCCESS! Assignment Verified!")
            print("=" * 60)
            print(f"\n{data.get('message', '')}")

            if data.get('already_completed'):
                print("\n🔁 Step already completed — re-verified successfully!")

            if data.get('next_step'):
                print(f"\n🚀 Step {data['next_step']} unlocked!")

            print("\n👉 Return to CrekAI")
            print("=" * 60)

        elif response.status_code == 400:
            message = data.get("message", "")
            if "Re-verification failed" in message:
                print("⚠️ Re-verification failed")
                print("\nYou already passed earlier, but your new code's output doesn't match the correct one.")
            else:
                print("❌ Validation Failed")
                print(f"\n{message or 'Check your code carefully'}")

        elif response.status_code == 401:
            print("❌ Invalid Token - Please regenerate your token in CrekAI.")

        else:
            print(f"❌ Unexpected Error ({response.status_code})")
            print(data.get("error", "Something went wrong."))

    except Exception as e:
        print(f"❌ Error: {e}")