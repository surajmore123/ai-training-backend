# Deployment and Environment Setup Training Module

This module standardizes the process for local setup, continuous integration (CI) workflow interaction, and environment verification across Development, Staging, and Production.

---

## I. Overview

The goal of this training is to ensure all team members understand the lifecycle of code from local commit to final production deployment, maintaining environment integrity and predictability.

### Key Environment Definitions

| Environment | Purpose | Access | Policy |
| :--- | :--- | :--- | :--- |
| **DEV** (Development) | Individual developer testing and feature integration. Unstable. | Restricted internal access (VPN required). | Frequent, automated deployments on every successful merge to `develop` branch. |
| **STAGING** | QA, User Acceptance Testing (UAT), and pre-production regression testing. | Internal and select stakeholder access. Mirror of Production data (anonymized). | Deployments triggered manually by CI/CD pipeline following successful DEV bake-in. **Required pre-requisite for Production.** |
| **PROD** (Production) | Live environment serving end-users. | Public access. Live data. | Manual deployment trigger, requiring mandatory sign-off from Engineering Lead and Product Owner. |

### Core Tools Utilized

*   **Version Control:** Git/GitHub
*   **Containerization:** Docker (All services are containerized)
*   **CI/CD Pipeline:** GitLab CI / GitHub Actions (Specify which tool is used)
*   **Infrastructure:** Kubernetes (For orchestration and deployment management)

---

## II. Step-by-Step Guidance: The Deployment Lifecycle

This section details the standard path for deploying a new feature or fix.

### Step 1: Local Environment Setup and Verification

1.  **Prerequisites Check:** Ensure Docker Desktop/Engine is running and configured correctly.
2.  **Clone Repository:** Fetch the latest version of the target repository (`git clone [repo_url]`).
3.  **Local Build:** Execute the standardized local build script (`make local-up` or equivalent) to build images and spin up services using `docker-compose`.
4.  **Verification:** Confirm all services are running without errors and access the application via `localhost:[port]`.
5.  **Environment Variable Check:** If adding a new variable, ensure it is added to the local `.env` file and committed to the centralized environment management system (e.g., Kubernetes ConfigMap definition).

### Step 2: Code Integration and CI Trigger

1.  **Feature Branch Creation:** Work must be done on a dedicated feature branch (`feature/XYZ`).
2.  **Testing:** Run all local unit tests (`make test`) and ensure 100% test pass rate locally.
3.  **Commit and Push:** Commit changes and push the feature branch to the remote repository.
4.  **Pull Request (PR) Submission:** Open a PR targeting the `develop` branch.
5.  **Automated CI Trigger:** The PR submission automatically triggers the CI pipeline which executes:
    *   Linter checks
    *   Security scans
    *   Unit and Integration tests
    *   Image building (Docker image creation and tagging)

### Step 3: Deployment to DEV Environment

1.  **Merge to Develop:** Once the PR is reviewed and approved, merge it into the `develop` branch.
2.  **Automated Deployment:** The merge triggers the CD process, which automatically deploys the newly built image to the DEV Kubernetes cluster.
3.  **Validation:** Access the DEV URL and perform basic smoke testing to ensure the service is responsive.

### Step 4: Promotion to STAGING (QA/UAT Gate)

1.  **Manual Trigger:** Navigate to the CI/CD pipeline interface (e.g., GitLab Jobs).
2.  **Select Staging Job:** Manually trigger the "Deploy to STAGING" job, selecting the verified image tag from DEV.
3.  **QA Cycle:** The QA team performs comprehensive regression and feature verification.
4.  **Sign-Off:** QA/PO provides formal sign-off confirming stability and readiness for Production.

### Step 5: Production Deployment

1.  **Branch Synchronization:** If using a Git Flow model, ensure `staging` or `master` branch is updated with the stable code.
2.  **Final Approval:** Ensure all necessary approvals (Lead Engineer, Product Owner) are documented in the deployment ticket.
3.  **Manual Execution:** Manually execute the "Deploy to PROD" job, selecting the approved image tag.
4.  **Post-Deployment Monitoring:** Monitor application health, error rates, and key metrics immediately following deployment.

---

## III. Common FAQs and Troubleshooting

| Question | Answer/Resolution |
| :--- | :--- |
| **My local build is failing with "missing dependency."** | Ensure your local setup is using the correct environment variables (`.env` file) and that all required package dependencies are listed in `package.json` or `requirements.txt`. Run `docker system prune -a` to clean cached images and rebuild. |
| **CI pipeline fails the test step but passes locally.** | This is typically an environment configuration issue (missing CI secret, different OS behavior, or race condition). Check the CI log output carefully for the exact error message and compare the CI build environment configuration against your local Docker setup. |
| **How do I view application logs for DEV/STAGING?** | Access the designated cloud platform dashboard (e.g., AWS CloudWatch, GCP Logging) or use the dedicated CLI tool (e.g., `kubectl logs [pod_name] -n [namespace]`). |
| **I need to add a new secret/environment variable.** | **Do NOT hardcode.** Update the centralized secret management system (e.g., HashiCorp Vault, Kubernetes Secrets) and then update the specific environment definition files (ConfigMaps) for DEV, STAGING, and PROD. |
| **Can I deploy directly to PROD for an emergency hotfix?** | The policy requires a successful run through STAGING for stability verification. If urgency is critical, a minimal STAGING test run must still be performed, followed by immediate required approvals. Documentation of the bypass/expedited process is mandatory. |

---

## IV. Role-Based Learning

### A. Backend Engineer Focus

Backend engineers are responsible for service reliability, resource consumption, and proper configuration management within the containers.

| Key Actions | Learning Focus |
| :--- | :--- |
| **Dockerfile Management** | Optimize Dockerfiles for speed and size (multi-stage builds). Ensure necessary dependencies are installed correctly and securely. |
| **Health Checks** | Implement robust readiness and liveness probes in the application code and configure them accurately in the Kubernetes deployment manifest. |
| **Environment Parity** | Use the `dev` environment strictly as a mirror of `staging`/`prod` variables (where secure). Ensure all environment variables are sourced from ConfigMaps, not hardcoded. |
| **Logging & Metrics** | Implement structured logging (JSON format recommended) that is easily ingestible by the monitoring stack (e.g., Prometheus, Datadog). |

### B. Frontend Engineer Focus

Frontend engineers must ensure the build process correctly handles asset bundling, caching, and serving across different environments.

| Key Actions | Learning Focus |
| :--- | :--- |
| **Build Artifact Integrity** | Verify that the CI process correctly generates minified, optimized static assets and places them in the correct location for containerization (e.g., `/usr/share/nginx/html`). |
| **Caching Strategy** | Understand how the CDN (if applicable) interacts with the deployment. Implement proper cache-busting strategies (e.g., content hashing of filenames) to ensure users see the latest version. |
| **Environment Switching** | Test dynamic configuration loading. The frontend must correctly detect whether it is running on DEV, STAGING, or PROD to connect to the correct backend APIs. |
| **CORS and Proxying** | Ensure all necessary Cross-Origin Resource Sharing (CORS) headers and proxy rules are defined in the configuration (e.g., Nginx config within the container) for each environment. |

### C. QA Engineer Focus

QA engineers are the gatekeepers of environment integrity and stability, primarily focusing on the STAGING environment.

| Key Actions | Learning Focus |
| :--- | :--- |
| **Deployment Verification** | Know how to trigger a specific build version/tag for deployment to STAGING to verify a bug fix or feature. |
| **Environment Access** | Maintain up-to-date bookmarks or configurations for accessing DEV, STAGING, and specific test environment URLs, including required VPN/authentication steps. |
| **Bug Reporting Detail** | When reporting environment-specific bugs, always include: **Environment Name** (DEV/STAGING), **Commit Hash/Image Tag**, and the exact **Time of Testing**. |
| **Resource Monitoring** | Utilize provided monitoring dashboards (e.g., Grafana, Kibana) to confirm application resource usage and error rates are stable during a testing cycle on STAGING. |