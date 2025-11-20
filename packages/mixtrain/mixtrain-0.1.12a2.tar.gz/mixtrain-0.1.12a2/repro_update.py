
import os
from unittest.mock import MagicMock, patch
from mixtrain.client import MixClient

def test_update_workflow_files():
    # Mock environment variables
    with patch.dict(os.environ, {"MIXTRAIN_API_KEY": "test-key", "MIXTRAIN_PLATFORM_URL": "http://test.com"}):
        client = MixClient()
        
        # Mock _make_request to inspect arguments
        client._make_request = MagicMock()
        client._make_request.return_value.json.return_value = {"data": {}}
        
        # Create dummy files
        with open("workflow.py", "w") as f:
            f.write("print('workflow')")
        with open("utils.py", "w") as f:
            f.write("print('utils')")
            
        try:
            # Call update_workflow
            client.update_workflow(
                workflow_name="test-workflow",
                workflow_file="workflow.py",
                src_files=["utils.py"],
                name="new-name"
            )
            
            # Verify arguments passed to _make_request
            call_args = client._make_request.call_args
            method = call_args[0][0]
            url = call_args[0][1]
            kwargs = call_args[1]
            
            print(f"Method: {method}")
            print(f"URL: {url}")
            
            if "files" in kwargs:
                files = kwargs["files"]
                print("Files argument type:", type(files))
                print("Files argument content:", files)
                
                # Verify structure
                if isinstance(files, list):
                    print("SUCCESS: files is a list")
                    # Check if it contains tuples
                    if all(isinstance(item, tuple) for item in files):
                        print("SUCCESS: files contains tuples")
                    else:
                        print("FAILURE: files contains non-tuples")
                else:
                    print("FAILURE: files is not a list")
            else:
                print("FAILURE: files argument missing")
                
        finally:
            # Cleanup
            if os.path.exists("workflow.py"):
                os.remove("workflow.py")
            if os.path.exists("utils.py"):
                os.remove("utils.py")

if __name__ == "__main__":
    test_update_workflow_files()
