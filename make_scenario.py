import requests

def send_to_webhook( emails:list, transcript:list) -> dict:
    """
    Sends a dictionary to a Make.com webhook using a POST request.

    Args:
        webhook_url (str): The Make.com webhook URL.
        data (dict): The dictionary to send.

    Returns:
        dict: Response status and message from the webhook.
    """
    webhook_url = "https://hook.eu2.make.com/c1e8g64lgtwo2zqeija4xfnejyt6tmnt"
    
    data={
        "emails": emails,
        "trancript": transcript 
        }
    try:
        # Ensure the data is in JSON format
        response = requests.post(webhook_url, json=data, headers={'Content-Type': 'application/json'})
        
        # Check the response status
        if response.status_code == 200:
            return {"status": "success", "message": response.json()}
        else:
            return {"status": "error", "message": response.text, "code": response.status_code}
    except requests.RequestException as e:
        return {"status": "error", "message": str(e)}

# Example usage
if __name__ == "__main__":
    # Replace with your actual Make.com webhook URL
    webhook_url = "https://hook.eu2.make.com/c1e8g64lgtwo2zqeija4xfnejyt6tmnt"
    # Example dictionary to send
    emails= ["anjaneyparasar14@gmail.com","ganujigarg@gmail.com"] 
    transcripts= [
            {
                "role": "assistant",
                "content": "Hello!  Welcome to your visa consultation.  Can we go ahead and discuss your visa roadmap?"
            },
            {
                "role": "user",
                "content": "Yeah. Sure."
            },
            {
                "role": "assistant",
                "content": "Great!  Let's get started with the first section of your roadmap. \n Initially, we'll determine the type of visa that best suits your needs.  This is based on your"
            },
            {
                "role": "user",
                "content": "Got it. Just give me a second. I'll"
            },
            {
                "role": "assistant",
                "content": "Of course, take your time!  Let me know when you're ready to continue."
            }
    ]

    data={
        "emails":["anjaneyparasar14@gmail.com","ganujigarg@gmail.com"] ,
        "transcripts": [
            {
                "role": "system",
                "content": "You are a visa expert whose role is to explain to the client their visa roadmap, which was drafted by a solution architect. Here's how the conversation will flow:\n\nGreet the client and ask if you can proceed to their roadmap.\nWait for their confirmation before starting.\nExplain the roadmap one section at a time.\nPause after each section to ensure the client understands. Ask if they are following along or if they have any questions.\nAnswer any questions briefly and continue when they are ready.\nAvoid jargon unless necessary. Use simple language and keep explanations short.\nSpeak naturally donn't use special symbols. \nstring",
                "name": "system"
            },
            {
                "role": "assistant",
                "content": "Hello!  Welcome to your visa consultation.  Can we go ahead and discuss your visa roadmap?"
            },
            {
                "role": "user",
                "content": "Yeah. Sure."
            },
            {
                "role": "assistant",
                "content": "Great!  Let's get started with the first section of your roadmap. \n Initially, we'll determine the type of visa that best suits your needs.  This is based on your"
            },
            {
                "role": "user",
                "content": "Got it. Just give me a second. I'll"
            },
            {
                "role": "assistant",
                "content": "Of course, take your time!  Let me know when you're ready to continue."
            }
    ]
    }

    result = send_to_webhook(emails, transcripts)
    print(result)
