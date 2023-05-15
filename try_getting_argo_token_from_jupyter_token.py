import requests

# from jwcrypto.jwt import JWT

# Step 1: Obtain the access token from the auth_state
# auth_state = get_auth_state_from_cookies()
# access_token = auth_state['access_token']
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJqeWY2bHdpY3gyR3BYbFByRGVWTGMzcnUyUmUzN0prZWhBNW9BbWtrLTBvIn0.eyJleHAiOjE2ODQwMzcwOTYsImlhdCI6MTY4NDAzNjc5NiwiYXV0aF90aW1lIjoxNjg0MDM2Nzk2LCJqdGkiOiIzZTFiODFlNC04ZmI5LTQ2NWUtYmZiMi1mYzQ0YzI4MjllMWYiLCJpc3MiOiJodHRwczovL2FkYW0yLm5lYmFyaS5kZXYvYXV0aC9yZWFsbXMvbmViYXJpIiwiYXVkIjpbInJlYWxtLW1hbmFnZW1lbnQiLCJhcmdvLXNlcnZlci1zc28iLCJjb25kYV9zdG9yZSIsImFjY291bnQiXSwic3ViIjoiZmE5ZWJkMzQtNDE2OC00NTI5LWIyZDMtOWMzMjk1NDIwYmZkIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoianVweXRlcmh1YiIsInNlc3Npb25fc3RhdGUiOiJlZjdmMTE0OC1lY2Y0LTRmNmUtYmU3Ny1mNmEwMDFiNWU0Y2QiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwiZGVmYXVsdC1yb2xlcy1uZWJhcmkiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7InJlYWxtLW1hbmFnZW1lbnQiOnsicm9sZXMiOlsibWFuYWdlLXVzZXJzIiwicXVlcnktZ3JvdXBzIiwicXVlcnktdXNlcnMiXX0sImp1cHl0ZXJodWIiOnsicm9sZXMiOlsiZGFza19nYXRld2F5X2FkbWluIiwianVweXRlcmh1Yl9hZG1pbiIsImp1cHl0ZXJodWJfZGV2ZWxvcGVyIl19LCJhcmdvLXNlcnZlci1zc28iOnsicm9sZXMiOlsiYXJnb192aWV3ZXIiLCJhcmdvX2FkbWluIl19LCJjb25kYV9zdG9yZSI6eyJyb2xlcyI6WyJjb25kYV9zdG9yZV9kZXZlbG9wZXIiLCJjb25kYV9zdG9yZV9hZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwic2lkIjoiZWY3ZjExNDgtZWNmNC00ZjZlLWJlNzctZjZhMDAxYjVlNGNkIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJyb2xlcyI6WyJtYW5hZ2UtdXNlcnMiLCJxdWVyeS1ncm91cHMiLCJxdWVyeS11c2VycyIsImRhc2tfZ2F0ZXdheV9hZG1pbiIsImp1cHl0ZXJodWJfYWRtaW4iLCJqdXB5dGVyaHViX2RldmVsb3BlciIsImFyZ29fdmlld2VyIiwiYXJnb19hZG1pbiIsImNvbmRhX3N0b3JlX2RldmVsb3BlciIsImNvbmRhX3N0b3JlX2FkbWluIiwibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdLCJuYW1lIjoiYWQgYWQiLCJncm91cHMiOlsiL2FkbWluIiwiL2FuYWx5c3QiXSwicHJlZmVycmVkX3VzZXJuYW1lIjoiYWQiLCJnaXZlbl9uYW1lIjoiYWQiLCJmYW1pbHlfbmFtZSI6ImFkIiwiZW1haWwiOiJhZEBhZC5jb20ifQ.czkRhvpQd-AY0JsgOWNoymMIYlwX_Ug10zbGRPibPhsuixwda0OL46Gfd5yeCNnP9yLmxr8N-45qs4uQGP6rh9GtwKKNwzeYtqtomFSBdfBoSwPAdyTeq0_eaeMb0WRlMD_CIY6IpRRrc2y8LOWFZJY2rYaKTBP8oAWIubG4Iwq-nEIWl6ANk8xklI_mCqrk2zW8l2QRD_o1eUigfLZKySJ_vjby-CWEY8K29K6W7WlblRKLG4vNvc6QPKYLbb4sBW6iEoWvSxLOQQ09FgpS9RPLLlIX43UfNbn161hw1LAbr9E5cXeM2Uxf7v2IuUT2WibZ6CEe_A8lRm2lZrp2Cg"
# claims = JWT().decode(access_token).claims

# Step 2: Use the access token to obtain an Argo Workflows token
# keycloak_token_url = 'https://keycloak.example.com/auth/realms/myrealm/protocol/openid-connect/token'
keycloak_token_url = (
    "https://adam2.nebari.dev/auth/realms/nebari/protocol/openid-connect/token"
)

# https://adam2.nebari.dev/auth/realms/nebari/protocol/openid-connect/auth?client_id=argo-server-sso&redirect_uri=https%3A%2F%2Fadam2.nebari.dev%2Fargo%2Foauth2%2Fcallback&response_type=code&scope=roles+openid&state=bff745fc1d
payload = {
    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
    "assertion": access_token,
    "client_id": "argo-server-sso",
    # 'client_secret': 'myclientsecret',
    # 'audience': 'argocd-api'
}
response = requests.post(keycloak_token_url, data=payload)
response.raise_for_status()
argocd_token = response.json()["access_token"]

# Step 3: Set the Argo Workflows token as an environment variable
config_map = {
    "apiVersion": "v1",
    "kind": "ConfigMap",
    "metadata": {"name": "myconfigmap"},
    "data": {"ARGOCD_AUTH_TOKEN": argocd_token},
}

# Create the ConfigMap in Kubernetes
create_config_map(config_map)

# Mount the ConfigMap as a volume in the JupyterLab pod
volume_mount = {"name": "myconfigmap", "mountPath": "/mnt/config"}

pod_spec = {
    # ... other pod configuration ...
    "spec": {
        "volumes": [volume_mount],
        "containers": [
            {
                # ... container configuration ...
                "volumeMounts": [volume_mount]
            }
        ],
    }
}
