# Training Material: Implementing the New Asynchronous Notification System (Project HSBASBH)

This document converts the key decisions and deliverables from the recent discussion into structured training material for implementing the new, scalable asynchronous notification system.

---

## I. Overview

The goal of Project HSBASBH is to transition our current synchronous, poll-based notification service to a highly performant, real-time asynchronous architecture (utilizing technologies like WebSockets and message queues). This shift will significantly improve user experience, reduce strain on primary API endpoints, and allow for immediate delivery of critical updates.

| Feature | Old System | New Asynchronous System |
| :--- | :--- | :--- |
| **Delivery Mechanism** | Polling (HTTP GET requests) | Real-Time Push (WebSockets/SSE) |
| **Latency** | High (based on poll interval) | Low (< 50ms) |
| **Server Load** | Constant, resource-intensive polling | Event-driven, efficient |
| **Integrity** | Potential for missed messages during drops | Guaranteed message delivery (via queue/fallback) |

### Key Goals for This Sprint

1.  Establish a stable WebSocket connection endpoint.
2.  Develop robust message serialization and deserialization across the stack.
3.  Implement client-side reconnection and fallback logic.
4.  Achieve a P95 notification latency of under 100ms in production.

---

## II. Step-by-Step Guidance: Implementation Workflow

This section outlines the chronological process for development, testing, and deployment of the new notification system.

### Step 1: Backend Service Definition and Setup (Days 1-3)

1.  **Queue Configuration:** Finalize the configuration and provisioning of the message queue (e.g., Kafka topic or RabbitMQ exchange) dedicated to notifications.
2.  **Gateway Development:** Create the dedicated Notification Gateway service responsible for handling incoming WebSocket connections and forwarding messages from the queue to the correct client session.
3.  **API Contract:** Define the specific notification JSON schema (`NotificationType`, `Payload`, `Timestamp`, `RecipientID`).
4.  **Documentation:** Publish the finalized WebSocket endpoint URL and expected authentication headers (e.g., token passing).

### Step 2: Frontend Client Integration (Days 4-6)

1.  **Connection Manager:** Develop the `NotificationConnectionManager` component responsible for initializing the WebSocket connection.
2.  **Authentication:** Implement the logic to securely pass the necessary authentication token during the connection handshake.
3.  **Listener Registration:** Create listeners within the frontend application state (e.g., Redux or Zustand) to consume incoming messages and update the UI accordingly.
4.  **Error Handling:** Implement mandatory client-side reconnection strategies (e.g., exponential backoff upon connection failure).

### Step 3: End-to-End Functional Testing (Days 7-8)

1.  **Integration Tests:** Backend and Frontend teams run joint tests to ensure successful message flow from the queue producer, through the Gateway, to the client browser.
2.  **Functional Scenarios:** QA engineers test all defined notification types (e.g., "Account Update," "New Message," "System Alert") to verify correct payload parsing and display.

### Step 4: Load and Resiliency Testing (Days 9-10)

1.  **Load Simulation:** QA and Backend collaborate on simulating high traffic (e.g., 5,000 concurrent connections) to test the Gateway's resilience.
2.  **Failure Modes:** Test scenarios involving temporary network disconnects, invalid authentication attempts, and rapid message bursts to confirm reconnection logic works correctly.

### Step 5: Deployment and Monitoring

1.  **Phased Rollout:** Deploy the new service behind a feature flag or use a controlled canary release.
2.  **Telemetry:** Configure real-time logging and metrics dashboards to track key performance indicators (KPIs) like connection time, message delivery latency, and disconnect rates.
3.  **Deprecation:** Schedule the deprecation of the legacy polling endpoints only after 100% successful adoption of the new asynchronous service.

---

## III. Common FAQs

| Question | Answer |
| :--- | :--- |
| **How do we handle connection dropouts?** | The client must implement an exponential backoff retry mechanism (e.g., 1s, 2s, 4s, 8s max). After `N` failed attempts, the user must be prompted to refresh the page or check their network. |
| **Are notifications stored if the user is offline?** | Yes. The message queue system acts as the temporary store. Upon connection, the user should make a fallback request to the REST API `/notifications/history` to retrieve missed messages from the database (which the Gateway service inserts into). |
| **What is the authentication method?** | WebSocket connections must pass a short-lived token (JWT) via a query parameter or header during the initial handshake. Long-running connections should utilize periodic token refreshing if required by security policy. |
| **Can we use this for large data transfer?** | No. This service is optimized for small, immediate alerts and metadata. Large payloads (e.g., images, document links) should be referenced via ID, requiring the client to fetch them via a standard REST API call. |
| **How can I test the queue locally?** | Docker Compose configurations have been provided in the root repository to spin up a local development instance of the message broker (e.g., `docker-compose up broker`). |

---

## IV. Role-Based Learning

### A. Backend Engineer Focus

The Backend team is responsible for infrastructure stability, message integrity, and scalability.

| Area of Focus | Key Deliverables & Actions |
| :--- | :--- |
| **Gateway Scalability** | Implement horizontal scaling capabilities for the Notification Gateway service. Ensure connection persistence is handled by sticky sessions or centralized state management (e.g., Redis). |
| **Message Resilience** | Configure the message queue with dead-letter queues (DLQs) for failed delivery attempts. Define the message serialization standard (e.g., Protocol Buffers vs. JSON). |
| **Security** | Validate the incoming authentication token on every connection attempt. Implement rate limiting to prevent denial-of-service attacks on the WebSocket endpoint. |
| **Database Integration** | Ensure the Gateway service successfully logs all outgoing notifications to the persistent database store for history retrieval (the `/notifications/history` endpoint). |

### B. Frontend Engineer Focus

The Frontend team is responsible for reliable connectivity, efficient state management, and user experience.

| Area of Focus | Key Deliverables & Actions |
| :--- | :--- |
| **Client Connection Logic** | Develop a dedicated hook or utility function (`useNotificationSocket()`) that abstracts connection, disconnection, and reconnection logic away from UI components. |
| **State Management** | Optimize listeners to prevent unnecessary re-renders when a message arrives. New notifications must be merged efficiently into the main application state without blocking the UI thread. |
| **UX & Throttling** | Implement visual feedback for connection status (e.g., "Connecting..." banner if the retry count is high). Throttle updates for non-critical notifications to avoid user annoyance (e.g., only show the badge count update every 5 seconds). |
| **Browser Compatibility** | Verify successful WebSocket implementation across all supported browsers (Chrome, Firefox, Safari, Edge). |

### C. QA Engineer Focus

The QA team is responsible for verifying functional correctness, non-functional performance, and system robustness.

| Area of Focus | Key Deliverables & Actions |
| :--- | :--- |
| **Functional Verification** | Use dedicated test accounts to trigger notifications from various upstream services (e.g., Payment service, Messaging service) and verify the correct message schema is received by the client. |
| **Performance Testing** | Utilize load testing tools (e.g., JMeter, K6) to simulate high concurrent connections (e.g., 10k users) and measure connection stability and message latency under stress. |
| **Integrity Testing** | Develop tests to deliberately disrupt the connection (e.g., disable/enable network interface) and confirm that the client successfully reconnects and retrieves any missed messages via the fallback history API. |
| **Security Testing** | Test edge cases like sending invalid or malicious payloads to the Gateway to ensure the service rejects them gracefully without crashing or corrupting data. |