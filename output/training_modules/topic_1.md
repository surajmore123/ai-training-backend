# API Authentication Training Module: Backend Services and Client Access

This training module converts discussions from recent meetings regarding API authentication standards, common integration issues, and essential knowledge for new team members across engineering disciplines.

---

## 1. Overview

This module defines the standard protocol for authenticating requests to our backend APIs. We utilize **Bearer Tokens** (specifically JSON Web Tokens or JWTs) transmitted securely over HTTPS.

The core principle is **stateless authentication**, where the token contains all necessary information (user ID, roles, expiry time) for the receiving API to validate the request without querying a central session store.

### Key Authentication Requirements

| Requirement | Description |
| :--- | :--- |
| **Protocol** | HTTPS/TLS required for all API communications. |
| **Token Type** | Bearer Token (JWT format). |
| **Transmission** | Via the `Authorization` header. |
| **Validation** | Must validate token signature, expiration, and required scopes/claims. |
| **Error Handling** | Standardized use of HTTP 401 (Unauthorized) and 403 (Forbidden). |

---

## 2. Step-by-Step Guidance: Standard Authentication Flow

This sequence outlines the process from client initiation to API resource access.

### Phase 1: Token Acquisition (Login/Client Credentials Grant)

1.  **Client Request:** The client (Frontend application, Mobile app, or another Backend Service) sends credentials (username/password or Client ID/Secret) to the designated **Authentication Server** (`/auth/token`).
2.  **Server Validation:** The Authentication Server verifies the credentials.
3.  **Token Generation:** The Auth Server generates a signed JWT (Access Token and usually a Refresh Token).
4.  **Token Return:** The Auth Server responds with the Access Token.

### Phase 2: API Request and Transmission

5.  **Client Storage:** The client securely stores the received Access Token.
6.  **Request Construction:** For every subsequent API call to a protected resource, the client must include the Access Token in the request header.

    ```
    // Example Header:
    Authorization: Bearer <Your_Generated_JWT>
    ```

7.  **Transmission:** The request is sent over HTTPS to the Target API (e.g., `/api/v1/users`).

### Phase 3: Backend Validation

8.  **Middleware Interception:** The Target API's authentication middleware intercepts the request.
9.  **Header Extraction:** The middleware extracts the token from the `Authorization` header.
10. **Validation Checks:** The middleware performs the following checks in sequence:
    *   Is the token present and correctly formatted?
    *   Is the token signature valid (signed by the expected Authority)?
    *   Is the token expired (`exp` claim)?
    *   Does the token contain the required scope/claims for this specific resource?
11. **Outcome:**
    *   **Success (Valid Token):** Request proceeds to the business logic handler.
    *   **Failure (Invalid Token/Format):** Middleware terminates the request with a `401 Unauthorized`.
    *   **Failure (Missing Permissions/Scope):** Middleware terminates the request with a `403 Forbidden`.

---

## 3. Common FAQs and Troubleshooting

| FAQ | Resolution and Explanation |
| :--- | :--- |
| **What is the difference between HTTP 401 and 403?** | **401 Unauthorized:** The client is not authenticated (e.g., missing, expired, or malformed token). The client *can* authenticate to proceed. **403 Forbidden:** The client *is* authenticated, but does not have the necessary permissions (scopes/roles) to access the specific resource. |
| **My token is valid, but I'm getting a 403 error.** | Check the JWT payload (using a tool like `jwt.io` or logs) for the `scopes` or `roles` claim. The required scope defined in the API endpoint must match a scope present in your token. |
| **Why is my token sometimes rejected even immediately after generation?** | Ensure there is no significant clock drift between the server generating the token (issuing time `iat`) and the server validating the token. If drift is unavoidable, ensure the validation middleware allows a few seconds of clock skew tolerance. |
| **Where should Frontend/SPA applications store the Access Token?** | **Avoid Local Storage.** This is vulnerable to XSS attacks. The preferred method is using **HTTP-Only, Secure Cookies**. If necessary to use memory/session storage, ensure strict Content Security Policies (CSP) are enforced. |
| **Do we use API Keys instead of Bearer Tokens?** | No. API Keys are static, less secure, and typically used for identifying a *client application*, not authenticating an *individual user* or granting time-limited access. Our standard is time-limited, signed Bearer Tokens. |
| **How long are tokens valid for?** | Access tokens are typically short-lived (5-15 minutes). This limits the window of opportunity if a token is compromised. Frontend clients must implement a **Token Refresh Flow** using the longer-lived Refresh Token before the Access Token expires. |

---

## 4. Role-Based Learning Objectives

Authentication implementation and testing involve different responsibilities depending on the engineering role.

### A. Backend Engineer Focus (API Implementation & Security)

**Core Responsibilities:**
*   Implement and configure the API gateway or application middleware responsible for validation.
*   Define the required scopes (`scope` claim) for each protected route.
*   Ensure cryptographic security (secure key rotation, proper JWT secret management).

| Task/Objective | Checklist/Action Item |
| :--- | :--- |
| **Validation Logic** | Integrate the standard authentication library (e.g., Passport.js, Spring Security, etc.) to handle signature verification and expiry checks. |
| **Scope Enforcement** | Implement authorization guards/decorators that check the incoming token's claims against the required route permissions. |
| **Key Management** | Ensure the public key used for signature verification is retrieved securely (e.g., from the Identity Provider's JWKS endpoint or secure configuration). |
| **Rate Limiting** | Implement authentication-aware rate limiting to prevent token-based brute-forcing or denial-of-service attempts. |

### B. Frontend Engineer Focus (Client Integration & User Experience)

**Core Responsibilities:**
*   Securely acquire and store the access token.
*   Implement efficient token transmission (HTTP Interceptors).
*   Manage the user session lifecycle (refreshing tokens, handling expiry).

| Task/Objective | Checklist/Action Item |
| :--- | :--- |
| **HTTP Interceptors** | Configure the client (e.g., Axios, Fetch) to automatically attach the `Authorization: Bearer` header to all API requests. |
| **Error Handling** | Write logic to detect `401 Unauthorized` errors. If detected, attempt token refresh. If refresh fails, redirect the user immediately to the login screen. |
| **Secure Storage** | Utilize secure methods for token storage (HTTP-only cookies preferred) and ensure tokens are *never* logged or exposed in client-side code unless absolutely necessary for token extraction before transmission. |
| **Refresh Flow** | Implement the automated mechanism to use the Refresh Token to obtain a new Access Token seamlessly before the current one expires. |

### C. QA Engineer Focus (Testing and Compliance)

**Core Responsibilities:**
*   Validate the robustness of the authentication and authorization mechanism.
*   Test expected failure modes to ensure correct HTTP status codes are returned.
*   Perform security/vulnerability checks.

| Task/Objective | Checklist/Action Item |
| :--- | :--- |
| **Positive Testing** | Verify access to all protected endpoints using a valid, fully scoped token. |
| **Negative Testing: 401** | Test API access using: 1) No token, 2) Expired token, 3) Token with a corrupted signature, 4) Token in the wrong format (`Bearer` keyword missing). All should return `401 Unauthorized`. |
| **Negative Testing: 403** | Test API access using a valid token that explicitly *lacks* the required scope/role for the resource. This must return `403 Forbidden`. |
| **Token Leakage Testing** | Check browser console logs and network traffic to ensure tokens are not inadvertently exposed (e.g., in URL query parameters or unsecured HTTP requests). |