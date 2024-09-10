**Devaj(V0.1)--an-AI-Web-Application**

**_This Project is made purely for personal use and Demonstration purposes and is only a quick demo of the funtionality_**

**Introduction**

Devaj(V0.1) is a custom AI chatbot designed for personal or family use within a local network (LAN) or globally through self-hosting. It leverages local inference APIs generated using tools like the LMS CLI or LM Studio's local server.

**Key Features**

- **Local LLM Model Integration:** Utilize your preferred local LLM model (e.g., Llama-3.1-8b) for a personalized chatbot experience.
- **LAN and Global Accessibility:** Deploy Devaj(V0.1) within your LAN for seamless family interaction, or extend its reach to limited external users by leveraging services like Zrok (depending on your system's capabilities).
- **Flexible Deployment Methods:** Choose between LM Studio's local server or self-hosting for optimal deployment based on your needs.

**Quick Demonstration using LM Studio**

1. **Clone the Repository:**
   ```git clone https://<your_github_url>/Devaj```

2. **Load Your LLM Model:**
   - Select a model compatible with your system's resources.
   - Follow LM Studio's instructions for model loading.

3. **Configuration Adjustments:**
   - In `app.py`, replace `https://localhost:5000/v1` with your LM Studio's local server address.
   - Edit Line 54 in `app.py`:
     ```
     model="your_model_api_identifier"  # Replace with your model's API identifier
     ```

4. **Run the Application:**
   - Install dependencies listed in `requirements.txt`.
   - Open `app.py` in VS Code.
   - Run `app.py`.

5. **Access the Chatbot:**
   - Open your browser and navigate to the Flask application's running address.
   - Login with username `admin` and password `123` (**credentials only for this demo, but needs a complete implementation of Account management**).

**Future Enhancements**

- **Account Management:** Implement a secure system for user creation and management.
- **Chat History Management:** Store and retrieve chat history for continuous conversations.
- **Detailed Documentation:** Provide comprehensive instructions for setup, configuration, and usage.
- **Security Measures:** Prioritize robust security measures to protect user data and prevent unauthorized access (especially when deployed outside your LAN). Consider replacing placeholder credentials and implementing authentication mechanisms.

**Testing and Deployment**

- Devaj(V0.1) has been successfully tested within a LAN and externally via Zrok by Globalizing the Local server ip and hosting the webapp on Render.
- External access performance may vary based on your system's capabilities and internet speed.

**Disclaimer**

This project is intended for personal and family use. It's recommended to prioritize security best practices, especially when deploying it outside your LAN. Consider the ethical implications.

**Additional Considerations**

- **Ethical Considerations:** Acknowledge the potential ethical implications of using a large language model for personal use.
