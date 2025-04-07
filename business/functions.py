from django.conf import settings 
from django.db.models import Count, Q
from datetime import  date, datetime, timedelta
from django.utils import timezone
from customers.models import Conversation, Customer, Interaction
import requests
import openai
from ai.models import TaskPipeline, Escalation, AI_Agent, SalesFunnelStageInstruction, AiReport,  Whatsapp, KnowledgeBase
from clients.models import Client
# from store.models import Product, PromotionalCampaign


# Set up OpenAI API key 
openai.api_key =settings.OPENAI_API_KEY

def receiveCall(audio):
    pass

def callClient(audio):
    pass


#######################################################################################################################################################
# sending message to whatsap
########################################################################################################################################################


def sendWhatsappMessage(client, fromId, message):
    whatsapp = Whatsapp.objects.filter(client=client).order_by("id").first()
    whatsapp_url = f'https://graph.facebook.com/v20.0/{whatsapp.whatsapp_phone_number_id}/messages'
    whatsapp_token =f'Bearer {whatsapp.whatsapp_auth_token}'
    headers = {"Authorization" : whatsapp_token}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type" : "individual",
        "to": fromId,
        "type":"text",
        "text":{"body": message}
        }
    requests.post(whatsapp_url, headers=headers, json=payload)
    return True


#######################################################################################################################################################
# ___________cutomer support agent________________________________
########################################################################################################################################################
    

# ductionary containing follow up instruction , depending on sales funnel stages 
FOLLOW_UP_INSTRUCTIONS = {
    'awareness': """
            Goal: Introduce your product/service.
            SOP:

            Research the target market and audience.
            Call, SMS, or WhatsApp the customer to introduce your product and its value.
            Keep the message short, highlighting a key problem and your solution.
            End with a clear CTA (e.g., schedule a call, visit website, or download resources).
            Log responses to track who shows interest for follow-up.
        """,
    'interest': """
            Goal: Engage prospects who show interest.
            SOP:
            Segment leads based on initial responses or missed calls.
            Call or WhatsApp them within 24-48 hours to follow up on their interest.
            Send personalized content via WhatsApp or SMS (e.g., case studies, testimonials).
            Offer to answer any questions or schedule a live demo.
            Track their engagement by noting call responses or content read in WhatsApp.
        """,
    'decision': """
            Goal: Help prospects evaluate and choose your solution.
            SOP:

            Call them to provide a tailored offer or clarify product features.
            Use WhatsApp or SMS to send product comparisons or limited-time promotions.
            Offer to schedule a one-on-one demo or consultation.
            Handle objections by discussing concerns over the call or sending clarifying information via SMS.
            Set up a follow-up call at a convenient time to keep the conversation going.
        """,
    'purchase': """
            Goal: Convert leads into paying customers.
            SOP:

            Call to guide them through the purchase process and confirm details.
            Use WhatsApp or SMS to provide payment links or instructions.
            Send a confirmation message once the purchase is completed.
            Offer immediate support through WhatsApp or phone to ensure a smooth transition.
            Request a review or referral via WhatsApp after successful onboarding.
        """,
    'active': """
            Goal: Retain and upsell existing customers.
            SOP:

            Call regularly to check on their satisfaction and ensure they’re utilizing the product fully.
            Send updates, new feature announcements, or upsell options through WhatsApp or SMS.
            Offer personalized promotions or loyalty discounts via phone or message.
            Provide a direct support line for them to contact you easily via phone or WhatsApp.
            Gather feedback through phone calls to strengthen the customer relationship.
        """,  
    'dormant': """
            Goal: Re-engage inactive customers.
            SOP:

            Identify dormant customers through CRM.
            Call to check in and remind them of your services.
            Send personalized re-engagement offers via WhatsApp or SMS.
            Highlight key benefits or provide a special offer to encourage action.
            Log responses from calls or messages and adjust future re-engagement strategies based on their feedback.
        """,  
}


# Define keywords or phrases that indicate the customer is busy
BUSY_KEYWORDS = [
    "busy", "call later", "can't talk now", "react out later", "later", "another time", "not now", "contact me next month"
]

def is_customer_busy(customer_message):
    """
    Check if the customer's message indicates they are busy.

    Parameters:
    - customer_message (str): The message from the customer.

    Returns:
    - bool: True if the customer is busy, False otherwise.
    """
    message = customer_message.lower()
    return any(keyword in  message for keyword in BUSY_KEYWORDS)

from django.utils import timezone


def get_company_knowledgebase(client):
    """
    Retrieve a company's products in an array format.

    Parameters:
    - customer (Customer object): The customer to retrieve products for.

    Returns:
    - tuple: A list of dictionaries with each dictionary containing product details,
             and a flag indicating if no products are found.
    """
    # Assuming Product has a foreign key to Company, which has a foreign key to Customer
    
    # client = Client.objects.filter(id=id).first()
    knwoledges = KnowledgeBase.objects.all(client=client)
    
    if not knwoledges.exists():
        return [], True
    
    # Build a list of product dictionaries
    company_products = [
        {
            "tite": knwoledge.title,
            "description": knwoledge.description,
            # Add other parameters as needed
        }
        for knwoledge in knwoledges
    ]
    
    return company_products, False


def get_past_conversations(client, customer):
    """
    Retrieve past conversation history for the given customer.

    Parameters:
    - customer (Customer object): The customer whose conversation history we want to retrieve.

    Returns:
    - str: A string representing the concatenated past conversation history.
    - bool: A flag indicating whether this is the customer's first interaction.
    """
    chats = Conversation.objects.filter(client=client, customer=customer).order_by('timestamp')
    
    if not chats.exists():
        # No previous chats, so it's the first interaction
        return "", True
    
    conversation_history = ""
    
    for chat in chats:
        if chat.sender =='customer':
            conversation_history += f"Customer: {chat.message}\n"
        else:
            conversation_history += f"AI: {chat.message}\n"
    
    return conversation_history, False


def save_conversation(client, customer, message, sender):
    # Save AI's response
    Conversation.objects.create(
        client=client,
        customer=customer,
        message=message,
        sender=sender
    )



def escalation_needed(client, agent, customer, customer_message, ai_response):
    """
    Check if the AI response indicates the need for escalation.

    Parameters:
    - ai_response (str): The response generated by the AI.

    Returns:
    - bool: True if escalation is needed, False otherwise.
    """
    escalation_keywords = ['escalate', 'help from human', 'support agent', 'can’t assist', 'need human']
    
    # Check if any escalation keyword is in the AI response
    if any(keyword in customer_message.lower() for keyword in escalation_keywords):
        escalate, created = Escalation.objects.get_or_create(customer=customer, client=client)
    
        # Assuming you have fields follow_up_date and follow_up_time in TaskPipeline
        escalate.reasons = customer_message
        escalate.save()
        if agent.escalation_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                customer_name = f'{customer.name} - phone number {customer.phone_number}' if customer.name else customer.phone_number
                message = f'i have escaleted {customer_name} i was unable to help, customers querry was: {customer_message}'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                customer_name = f'{customer.name} - phone number {customer.phone_number}' if customer.name else customer.phone_number
                message = f'i have escaleted {customer_name}i was unable to help, customers querry was {customer_message}'
                sendWhatsappMessage(client, fromId, message)

    elif any(keyword in ai_response.lower() for keyword in escalation_keywords):
        escalate, created = Escalation.objects.get_or_create(customer=customer, client=client)
    
        # Assuming you have fields follow_up_date and follow_up_time in TaskPipeline
        escalate.reasons = customer_message
        escalate.save()
        if agent.escalation_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                customer_name = f'{customer.name} - phone number {customer.phone_number}' if customer.name else customer.phone_number
                message = f'i have responded to {customer_name} query which was {customer_message}'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                customer_name = f'{customer.name} - phone number {customer.phone_number}' if customer.name else customer.phone_number
                message = f'i have responded to {customer_name} query which was {customer_message}'
                sendWhatsappMessage(client, fromId, message)
    return ''


def update_funnel_stage(customer, customer_message):
    """
    Update the customer's sales funnel stage based on their message.

    Parameters:
    - customer (Customer object): The customer record from the database.
    - customer_message (str): The latest message from the customer.

    Returns:
    - new_funnel_stage (str): Updated funnel stage for the customer.
    """
    if any(keyword in customer_message.lower() for keyword in ["interested","intrested", "details", "more information"]):
        new_funnel_stage = "interest"
    elif any(keyword in customer_message.lower() for keyword in ["ready", "purchase", "buy"]):
        new_funnel_stage = "decision"
        # update this other funnels stages later 
    # elif any(keyword in customer_message.lower() for keyword in ["ready", "purchase", "buy"]):
    #     new_funnel_stage = "purcahse"
    # elif any(keyword in customer_message.lower() for keyword in ["ready", "purchase", "buy"]):
    #     new_funnel_stage = "active"
    # elif any(keyword in customer_message.lower() for keyword in ["ready", "purchase", "buy"]):
    #     new_funnel_stage = "dormant"
    else:
        new_funnel_stage = customer.funnel_stage 

    # Update the funnel stage in the database (pseudo-code)
    customer.funnel_stage = new_funnel_stage
    customer.save()

    return new_funnel_stage



def handle_customer_query(client, customer, customer_message):
    """
    Handles a customer query, introducing yourself on the first interaction while responding to the query.

    Parameters:
    - customer_message (str): The new message from the customer.
    - customer_data (dict): Information about the customer, including name, company, and funnel stage.

    Returns:
    - AI response, new funnel stage, escalation flag
    """
    
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="sales agent")

    #company products 
    knwoledge , no_knwoledge = get_company_knowledgebase(client)
    

    # Get the past conversation history and check if it's the first interaction
    past_history, is_first_interaction = get_past_conversations(client, customer)

    # Prepare the introduction message if it's the first interaction
    if is_first_interaction:
        introduction_message = f"Hello! I’m {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'sales agent'}, your AI assistant working with {client.business_name if client and hasattr(client, 'company_name') else ''}. "
    else:
        introduction_message = ""

    
    instructions = SalesFunnelStageInstruction.objects.filter(client=client, funnel_stage=customer.funnel_stage).first()
    if  instructions is None:
        follow_up_instructions= FOLLOW_UP_INSTRUCTIONS.get(customer.funnel_stage, """
            Goal: Engage prospects who show interest.
            SOP:
            Segment leads based on initial responses or missed calls.
            Call or WhatsApp them within 24-48 hours to follow up on their interest.
            Send personalized content via WhatsApp or SMS (e.g., case studies, testimonials).
            Offer to answer any questions or schedule a live demo.
            Track their engagement by noting call responses or content read in WhatsApp.
        """)
    # Prepare the full prompt including the introduction if necessary
    if client.industry and client.industry.prompt: 
        prompt = f""" { client.industry.prompt}""" 
    else:
        prompt = f"""
        here is our: 
        company knowledge base : {knwoledge}.
        Act as an experienced AI real estate sales agent named {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'Sales Agent'}, working for {client.business_name} targeting clients looking for rental properties, first homes, or real estate investments. Your primary goal is to initiate and nurture meaningful conversations that guide clients to the right property options, adapting your responses based on the client’s stage in the decision-making process (exploring, evaluating, or ready to purchase). Use SPIN Selling, Influence, and The Challenger Sale frameworks to guide responses, tailoring to the following specifics:

        Customer Engagement and Questioning (SPIN Framework):

        Exploring Clients: Begin with Situation questions to gather context on what they are looking for (rental, first home, or investment).
        Evaluating Clients: Move into Problem and Implication questions to identify their specific needs and pain points (e.g., location preferences, budget constraints).
        Ready to Purchase Clients: Focus on Need-Payoff questions, highlighting how the AI can offer the best deals, investment opportunities, or rental options to save them time and money.
        Building Influence and Authority (Cialdini’s Principles):

        Reciprocity: Provide valuable insights such as market trends, advice on the home-buying process, or investment tips in return for their trust.
        Authority: Display expertise by referencing successful cases of clients finding their ideal properties or successful investment deals.
        Social Proof: Share success stories from clients who have successfully rented homes, purchased their first properties, or made profitable investments, tailored to their specific situation (e.g., first-time home buyers or rental seekers).
        Challenging Clients’ Perspectives (The Challenger Sale):

        For Clients Uncertain About Property Choices: Gently challenge their current thinking by introducing new possibilities or properties they may not have considered. Position the AI as a solution to help them discover hidden gems, better investment opportunities, or properties that align more closely with their needs.
        For Investment Seekers: Encourage clients to explore alternative investment strategies or properties with higher potential returns, focusing on market growth areas or emerging investment opportunities.
        Objection Handling and Escalation:

        Address objections about pricing, location, or property features with solution-oriented responses, offering alternatives that still meet their needs.
        If the client expresses concern about the AI’s recommendations or asks a complex question, escalate the conversation to a human real estate expert, offering to schedule a consultation with an agent for more tailored advice.
        Conversational Flow:

        Always ask follow-up questions to ensure engagement and move the conversation forward. Adapt follow-up questions based on the client’s responses, such as: “What’s your timeline for moving?” or “What’s most important to you when selecting a property?”
        If a client mentions a budget range, ask about their desired amenities or location to refine the search.
        Tailoring Responses to Specific Needs:

        For Rental Clients: Focus on rental prices, lease terms, amenities, and the neighborhood.
        For First-Time Homebuyers: Emphasize affordability, financing options, and proximity to work, schools, or family.
        For Real Estate Investors: Highlight ROI potential, investment strategies, property appreciation rates, and rental income.
        End Goal:

        Continuously steer the conversation towards a property recommendation or action step. Reiterate the AI's ability to simplify property searches, provide valuable market insights, and save time in finding the right match.
        Suggest next steps like scheduling a property tour, receiving property details, or discussing financing options with a human agent.
        Customer's name: {customer.name if customer and hasattr(customer, 'name') else 'customer'}.
        Below is the past conversation history: {past_history}
        Now, the customer said: "{customer_message}" 
        make the message consise and to the point, easy to profread and not more than 350 characters unless asked for indepth explanation
        make the message flow one th feels to have been wwritten by human and design for whatsapp chat
        """
    
    # Call OpenAI API to generate a response based on the dynamic prompt
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert AI sales Agent."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response
    ai_response = response['choices'][0]['message']['content']
    sender = "AI"
    message = ai_response
    save_conversation(client, customer, message, sender)

    # handle escalations
    escalation_needed(client, agent, customer, customer_message, ai_response)

    # handle Update funnel stage based on customer message (e.g., based on keywords like "interested")
    update_funnel_stage(client, customer, customer_message)

    
    if agent.respond_notification:
        if agent.whatsapp_number_1:
            fromId = agent.whatsapp_number_1
            customer_name = customer.name if customer.name else customer.phone_number
            message = f'i have responded to {customer_name} query which was {customer_message}'
            sendWhatsappMessage(client, fromId, message)
        if agent.whatsapp_number_2:
            fromId = agent.whatsapp_number_1
            customer_name = customer.name if customer.name else customer.phone_number
            message = f'i have responded to {customer_name} query which was {customer_message}'
            sendWhatsappMessage(client, fromId, message)
    return ai_response  


import re

def extract_time(message):
    """
    Extracts time from the message using regex to handle formats like '3pm', '15:00', etc.
    """
    time_pattern = r'(\d{1,2}(?::\d{2})?\s?(?:am|pm)?)'
    match = re.search(time_pattern, message, re.IGNORECASE)
    if match:
        return match.group(0)
    return None

def extract_follow_up_datetime(customer_message):
    """
    Extracts a follow-up date and time from the customer's message.
    
    Returns a datetime object or None if parsing fails.
    """
    customer_message = customer_message.lower()

    # Default follow-up date is today
    follow_up_date = datetime.now()

    # Check for keywords like 'tomorrow' and adjust the date
    if "tomorrow" in customer_message:
        follow_up_date = follow_up_date + timedelta(days=1)

    # You can add more logic for other keywords like "next week", etc.

    # Extract the time from the message
    time_str = extract_time(customer_message)

    if time_str:
        # Parse the time (e.g., '3pm' -> '15:00')
        follow_up_time = datetime.strptime(time_str, '%I%p' if 'pm' in time_str or 'am' in time_str else '%H:%M').time()
        follow_up_datetime = datetime.combine(follow_up_date, follow_up_time)
    else:
        # If no time is found, return the default date (just the day, no specific time)
        follow_up_datetime = follow_up_date

    print(f"Extracted datetime: {follow_up_datetime}")
    return follow_up_datetime


def update_follow_up_in_task_pipeline(task_pipeline, follow_up_datetime):
    """
    Updates the TaskPipeline for the customer with the provided follow-up time and date.

    Parameters:
    - customer: The customer object.
    - follow_up_date: The date for follow-up.
    - follow_up_time: The time for follow-up.

    Returns:
    - None
    """
    # Assuming you have fields follow_up_date and follow_up_time in TaskPipeline
    task_pipeline.follow_up_date = follow_up_datetime.date()
    task_pipeline.follow_up_time = follow_up_datetime.time()
    
    task_pipeline.save()

def extract_name(customer_message):
    # A simple regex pattern to match a name (capitalize the first letter)
    pattern = r'\b(?:my name is| | am |I am|I’m|my name’s| naitwa | najulikana kama| jina langu ni?)\s+([A-Z][a-z]+)\b'
    match = re.search(pattern, customer_message, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def handle_customer_query_with_follow_up(client, customer_message, fromId):
    """
    Handles a customer query, detecting if the customer is busy and handling follow-up scheduling.

    Parameters:
    - customer_message (str): The new message from the customer.
    - customer_data (dict): Information about the customer, including name and funnel stage.

    Returns:
    - AI response, updated funnel stage, escalation flag
    """
    #getting customer 
    customer = Customer.objects.filter(client=client, phone_number=fromId).order_by('id').first()
    if not customer:
        customer= Customer.objects.get_or_create(
                client=client,
                phone_number=fromId
            )
    #adding this to last time talked with the customer
    customer.last_talked = timezone.now().date()
    customer.save()
    #getting the previous chat 
    # previous_chat = Conversation.objects.filter(customer=customer ).order_by('-timestamp').first()
    # last_chat = previous_chat if previous_chat is not None else ""
    # Check if customer indicates they are busy
    # if cust
    if is_customer_busy(customer_message):
        # AI response asking for a convenient time and date
        ai_response = f"Thank you for letting me know! I appreciate your time. Could you please let me know a more convenient time and date for us to follow up?"

        # Save this interaction in the TaskPipeline for later follow-up
        task = f'follow up customer as was busy last time you reached out on {timezone.now().date()}'
        task_pipeline = TaskPipeline.objects.filter(client=client, customer=customer, done=False).first()
        if not  task_pipeline:
            TaskPipeline.objects.create(client=client, customer=customer, task=task)

        #  the above function was trying to extract time and date and be able to add it to task pipeline but it does not work 

        follow_up_datetime = extract_follow_up_datetime(customer_message)

        if follow_up_datetime:
            ai_response = f"Thank you! I have scheduled a follow-up for {follow_up_datetime.strftime('%A, %B %d at %I:%M %p')}."
            update_follow_up_in_task_pipeline(task_pipeline, follow_up_datetime)
        else:
            ai_response = "Sorry, I couldn't understand the follow-up time. Could you please provide a specific time and date?"

        return ai_response
   
    else:
        # wanted to extract name and save it
        # chat = Conversation.objects.filter(customer=customer, sender='AI').order_by('-id').first()
        # if chat:
        #     name_keywords = ['your name', 'share your name', 'know your name']
        #     if any(keyword in chat.lower() for keyword in name_keywords):
        #         if not customer.name:  # Only run if customer has no name
        #             name = extract_name(customer_message)
        #             if name:  # Check if a name was successfully extracted
        #                 customer.name = name
        #                 customer.save()
        
        return handle_customer_query(client,  customer, customer_message)



#bring it all together 
#lets define the function thart talk to webhook
def handleWhatsappCall(client, fromId, customer_message):
    message = handle_customer_query_with_follow_up(client, customer_message, fromId)
    sendWhatsappMessage(client, fromId, message)
    

#######################################################################################################################################################
# leads warmup agent
########################################################################################################################################################

# function that checks the last time customer was called and the add customer to TaskPipeline

# Define the minimum follow-up days for each funnel stage
FOLLOW_UP_DAYS = {
    'awareness': 5,
    'interest': 3,
    'decision': 2,
    'purchase': 1,
    'active': 7,   # Assuming 1-2 weeks; using the minimum of 7 days
    'dormant': 30  # Assuming 30-60 days; using the minimum of 30 days
}

def add_customers_to_pipeline(client):
    # Get the current date
    current_date = timezone.now().date()
    
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="sales agent")
    # Get all customers who haven't been talked to recently based on their funnel stage
    customers_to_follow_up = Customer.objects.filter(client=client)
    total_follow_up = 0
    # Iterate over each customer and determine if they need a follow-up
    for customer in customers_to_follow_up:
        # lets get how many days to follow up after last interaction
        instructions = SalesFunnelStageInstruction.objects.filter(client=client, funnel_stage=customer.funnel_stage).first()
        # Get the follow-up threshold based on the customer's funnel stage
        if instructions:
            days = instructions.days_to_follow_up
        else:
            days = FOLLOW_UP_DAYS.get(customer.funnel_stage, 3) # Default to 3 days if no stage matches
        follow_up_days = days  
        
        # Check if the last talked date exceeds the threshold
        if customer.last_talked <= current_date - timedelta(days=follow_up_days):
            # Check if the customer is already in the pipeline and the task is not done
            existing_task = TaskPipeline.objects.filter(client=client, customer=customer, done=False).exists()
            
            if not existing_task:  # Only add if no active task exists
                TaskPipeline.objects.create(
                    client=client,
                    customer=customer,
                    task = 'follow up with the customer',
                    follow_up_date=current_date, # + timedelta(days=1),  # Set follow-up date for the next day
                    follow_up_time=None,  # You can set a default time here if needed
                )
                total_follow_up +=1

    if total_follow_up == 0:
        if agent.follow_up_notification | agent.midday_report_notification | agent.evening_report_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                message = f'Hello!!! have {total_follow_up} customers to follow up with, please add customers to the database so than i can do my job'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                message = f'Hello!!! have {total_follow_up} customers to follow up with, please add customers to the database so than i can do my job'
                sendWhatsappMessage(client, fromId, message)
    else:
        if agent.follow_up_notification | agent.midday_report_notification | agent.evening_report_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                message = f'Hello!!! have only {total_follow_up} customers to follow up with, imagine if you can give me more, More follow-up equals more engagement which equals to more sales'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                message = f'Hello!!! have only {total_follow_up} customers to follow up with, imagine if you can give me more, More follow-up equals more engagement which equals to more sales'
                sendWhatsappMessage(client, fromId, message)           

# leads warmup agent
def follow_up_tasks_today(client):
    """
    This function checks all tasks in TaskPipeline that have a follow-up date of today
    and initiates a follow-up process for each of them.
    
    Returns:
    - A list of follow-up results for each customer.
    """
    
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="sales agent")

    #company products 
    knwoledge , no_knwoledge = get_company_knowledgebase(client)
    current_date=timezone.now().date()
    # Get all tasks with a follow-up date of today
    tasks_to_follow_up = TaskPipeline.objects.filter(client=client, follow_up_date=current_date, done=False).order_by('id')[:3]

    # Iterate over each task and follow up with the respective customer
    for task in tasks_to_follow_up:
        customer = task.customer
        
        # Get the past conversation history and check if it's the first interaction
        past_history, is_first_interaction = get_past_conversations(client, customer)

        # Prepare the introduction message if it's the first interaction
        if is_first_interaction:
            introduction_message = f"Hello! I’m {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'Sales Agent'}, your AI assistant working with {client.business_name if client and hasattr(client, 'company_name') else ''}. "
        else:
            introduction_message = ""

        # getting guidin sops depending on customer sales funnel stage
        instructions = SalesFunnelStageInstruction.objects.filter(client=client, funnel_stage=customer.funnel_stage).first()
        if not instructions:
            follow_up_instructions= FOLLOW_UP_INSTRUCTIONS.get(customer.funnel_stage, """
                Goal: Engage prospects who show interest.
                SOP:
                Segment leads based on initial responses or missed calls.
                Call or WhatsApp them within 24-48 hours to follow up on their interest.
                Send personalized content via WhatsApp or SMS (e.g., case studies, testimonials).
                Offer to answer any questions or schedule a live demo.
                Track their engagement by noting call responses or content read in WhatsApp.
            """)
        
        # Prepare the full prompt including the introduction if necessary
        if client.industry and client.industry.prompt: 
            prompt = f""" { client.industry.prompt}""" 
        else:
            prompt = f"""
            here is our: 
            company knowledge base : {knwoledge}.
            Customer's name: {customer.name if customer and hasattr(customer, 'name') else 'customer'}.
            Past conversation history: {past_history}
            Act as an experienced AI real estate sales agent named {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'Sales Agent'}, working for {client.business_name} targeting clients looking for rental properties, first homes, or real estate investments. Your primary goal is to initiate and nurture meaningful conversations that guide clients to the right property options, adapting your responses based on the client’s stage in the decision-making process (exploring, evaluating, or ready to purchase). Use SPIN Selling, Influence, and The Challenger Sale frameworks to guide responses, tailoring to the following specifics:

               Contextual Engagement and Questioning (SPIN Framework):

            Exploring Clients: Use Situation questions to re-establish contact and build rapport. Reference the last point in their search or inquiry, such as “Are you still interested in exploring properties in [location]?” or “Has anything changed in what you’re looking for since we last spoke?”

            Evaluating Clients: Transition to Problem and Implication questions to remind them of specific needs they previously mentioned, like budget or location. Engage by asking, “Have you come across any challenges in your search so far?” or “Would it help to explore options with better financing terms?”

            Ready to Purchase Clients: Emphasize Need-Payoff questions, focusing on the unique benefits of available properties. Keep the message short but impactful, such as “I found a property that checks off your requirements list—would you like more details?”

            Building Influence and Authority (Cialdini’s Principles):

            Reciprocity: Share value-driven insights, like “Just wanted to send you a quick update on rental trends in [location]—I think you’ll find it helpful!” or “Here’s a tip that might make your property search easier.”

            Authority: Reference successful experiences of similar clients who found their ideal properties with your help, positioning the AI as a knowledgeable assistant. E.g., “I recently helped a client find a great property near [landmark]—would you like to explore similar options?”

            Social Proof: Mention stories of satisfied clients in a similar situation. For example, “Many clients found value in looking at properties just outside the main area for better deals—would you like to check a few of these out?”

            Challenging Clients’ Perspectives (The Challenger Sale):

            For Clients Considering Alternative Options: Encourage them to reconsider overlooked opportunities by introducing new ideas or property types, e.g., “Have you considered [property type] in [neighborhood]? It might offer more value within your budget.”

            For Investment Seekers: Prompt a response by suggesting untapped market opportunities, such as “I found a property with promising ROI potential—are you interested in seeing the details?”

            Objection Handling and Re-engagement:

            Address Objections: If they had previous hesitations, respond with a solution-oriented message and include an invitation for further discussion. For example, “I know the location was a concern for you—would it help if we explored properties with better access to transit?”

            Escalate to Expert Assistance: For complex queries, smoothly offer to connect them with a real estate expert, e.g., “Would you like me to schedule a quick call with an agent to answer any specific questions?”

            Conversational Flow and Prompting Responses:

            Follow-Up Questions: Use follow-up questions based on previous conversations, such as “Are you still considering a move within [timeframe]?” or “Would a virtual tour make it easier to decide on some options?”

            Engagement and Action Triggers: End each message with an action-triggering question that makes it easy for clients to respond. Example: “What’s your preferred move-in date so we can narrow down options?” or “Which feature matters most to you—location or amenities?”

            Tailoring Responses to Specific Needs:

            For Rental Clients: Discuss lease terms, neighborhood amenities, and proximity to conveniences. Prompt with questions like “Is proximity to work still a priority for you?”

            For First-Time Homebuyers: Emphasize affordability and financing, with questions like “Would you like information on financing options for first-time buyers?”

            For Real Estate Investors: Focus on ROI, growth areas, and property appreciation rates. Engage with prompts like “Are you looking for properties with rental income potential?”

            End Goal:

            Drive Engagement: Keep responses open-ended but engaging, e.g., “Would you like me to send over a few options that meet your latest criteria?”

            Suggest Next Steps: Include gentle CTAs like, “How about a quick call to go over the options I found?” or “Would you like to schedule a viewing to get a feel for the area?"
            The message should be concise and brief and not more than 350 characters unless asked for indepth explanation.
         format it for whatsap conversation.
            """

        # Call OpenAI API to generate a response based on the dynamic prompt
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful AI sales assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        ai_response = response['choices'][0]['message']['content']

        # sending the follow up message 
        fromId = customer.phone_number
        message = ai_response
        sendWhatsappMessage(client, fromId, message)
        
        # Save AI's folow up message 
        Conversation.objects.create(
            client=client,
            customer=customer,
            message=ai_response,
            sender='AI'
        )
        # Mark the task as done (or update it as necessary)
        task.done = True
        task.save()
        if agent.follow_up_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                customer_name = customer.name if customer.name else customer.phone_number
                message = f'i have followed up with {customer_name}, our previous conversation was on {customer.last_talked}'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                customer_name = customer.name if customer.name else customer.phone_number
                message = f'i have followed up with {customer_name}, our previous conversation was on {customer.last_talked} '
                sendWhatsappMessage(client, fromId, message)
        # update last talked
        customer.last_talked = timezone.now().date()
        customer.save()

    return True

# leads warmup agent 2
def follow_up_immediately(id, fromId):
    """
    This function follow up with customer immediately after being added to the database.
    
    Returns:
    - A list of follow-up results for each customer.
    """
    client = Client.objects.filter(id=id).first()
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="sales agent")

    #company products 
    knwoledge , no_knwoledge = get_company_knowledgebase(client)
    # Iterate over each task and follow up with the respective customer
    customer = Customer.objects.filter(client=client, phone_number=fromId).first()
    interactions = Interaction.objects.filter(client=client, customer=customer).order_by('-id').first()
    
    if interactions:
        last_interaction_summary = interactions.conversation_summary
        if interactions.interaction_place == 'your shop':
            refferal_source = f'visited us at our shop'
        elif interactions.interaction_place == 'customers shop':
            refferal_source = f'reach out at {interactions.interaction_place}'
        elif interactions.interaction_place == 'call':
            refferal_source = f'reach out through {interactions.interaction_place}'
        else:
            refferal_source = f'i interacted with online'
    else:
        refferal_source=''
        last_interaction_summary=''
    chats = Conversation.objects.filter(client=client, customer=customer, sender='customer')
    if chats:
    # Get the past conversation history and check if it's the first interaction
        past_history= get_past_conversations(client, customer)
        
        # Prepare the full prompt including the introduction if necessary
        prompt = f"""
            our company knowledge base: {knwoledge}.
            customer past conversation history:{past_history}
            acting as an AI sales agent named {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'Sales Agent'}, 
            representing {client.business_name}.
            write a proffessional and personalized follow-up message to a customer named {customer.name}
            whose description is {customer.description}
            and our interaction summary is {last_interaction_summary}
            that i just {refferal_source}
            The message should be appreciative, warm and brief mentioning the interaction and expressing a desire to stay in touch and learn from each other.
            format it for whatsap conversation.

            """


        # Call OpenAI API to generate a response based on the dynamic prompt
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You an AI sales agent."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        ai_response = response['choices'][0]['message']['content']

        # sending the follow up message 
        message = ai_response
        sendWhatsappMessage(client, fromId, message)
        
        # Save AI's folow up message 
        Conversation.objects.create(
            client=client,
            customer=customer,
            message=ai_response,
            sender='AI'
        )
    else:
        if customer.niche :
            message = customer.niche.outreach_message
            sendWhatsappMessage(client, fromId, message)
            # Save AI's folow up message 
            Conversation.objects.create(
                client=client,
                customer=customer,
                message=message,
                sender='AI'
            )
        pass
    if agent.follow_up_notification:
            if agent.whatsapp_number_1:
                fromId = agent.whatsapp_number_1
                customer_name = customer.name if customer.name else customer.phone_number
                message = f'i have followed up with {customer_name}, who you have recently added to the database'
                sendWhatsappMessage(client, fromId, message)
            if agent.whatsapp_number_2:
                fromId = agent.whatsapp_number_1
                customer_name = customer.name if customer.name else customer.phone_number
                message = f'i have followed up with {customer_name}, who you have recently added to the database'
                sendWhatsappMessage(client, fromId, message)
        # update last talked
    customer.last_talked = timezone.now().date()
    customer.save()
    return True

# def immediatelyFollowUpWithCustomer(client, fromId):
#     message = follow_up_immediately(client, fromId)
#     sendWhatsappMessage(client, fromId, message)

def aiWorkReport(client):
    current_time = datetime.now().time()
    cutoff_time = datetime.strptime('18:00:00', '%H:%M:%S').time()
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="sales agent")
    if current_time >= cutoff_time:
        if AiReport.objects.filter(client=client, ai=agent).exists():
            
            today = date.today()
            last_update_instance = AiReport.objects.filter(client=client).first()
            if last_update_instance.last_updated < today:
                
                customers = Customer.objects.filter(client=client).annotate(unread_count=Count('conversations', filter=Q(conversations__read=False)))
                chats = Conversation.objects.filter(client=client, date_added=today, sender='AI').count()
                tasks = TaskPipeline.objects.filter(client=client, follow_up_date=today, done=True).count()
            
                last_update_instance.save()
                if agent.follow_up_notification | agent.midday_report_notification | agent.evening_report_notification:
                    if agent.whatsapp_number_1:
                        fromId = agent.whatsapp_number_1
                        message = f'Evening %OA Here is my Today Work Report %OA I have followed up with {tasks} customers %OA I have responded to {customers} customers %OA I have send a total of{chats} messages '
                        sendWhatsappMessage(client, fromId, message)
                    if agent.whatsapp_number_2:
                        fromId = agent.whatsapp_number_1
                        message = f'Evening %OA Here is my Today Work Report %OA I have followed up with {tasks} customers %OA I have responded to {customers} customers %OA I have send a total of{chats} messages '
                        sendWhatsappMessage(client, fromId, message)
            else:
                pass
        else:
            AiReport.objects.create(client=client, ai=agent, send = True)
            today = date.today()
            customers = Customer.objects.filter(client=client).annotate(unread_count=Count('conversations', filter=Q(conversations__read=False)))
            chats = Conversation.objects.filter(client=client, date_added=today, sender='AI').count()
            tasks = TaskPipeline.objects.filter(client=client, follow_up_date=today, done=True).count()
            if agent.follow_up_notification | agent.midday_report_notification | agent.evening_report_notification:
                if agent.whatsapp_number_1:
                    fromId = agent.whatsapp_number_1
                    message = f'Evening %OA Here is my Today Work Report %OA I have followed up with {tasks} customers %OA I have responded to {customers} customers %OA I have send a total of{chats} messages '
                    sendWhatsappMessage(client, fromId, message)
                if agent.whatsapp_number_2:
                    fromId = agent.whatsapp_number_1
                    message = f'Evening %OA Here is my Today Work Report %OA I have followed up with {tasks} customers %OA I have responded to {customers} customers %OA I have send a total of{chats} messages '
                    sendWhatsappMessage(client, fromId, message)
    else: 
        return


def chatbotResponse(client, user_message, history):
    """
    Generates a follow-up message for a customer based on user input and chat history.
    
    Parameters:
    - user_message: The latest message from the user.
    - history: List of past chat messages to provide context.
    
    Returns:
    - The AI-generated response.
    """
    # Retrieve company and agent information
    agent = AI_Agent.objects.filter(client=client).order_by('id').first()
    if not agent:
        agent = AI_Agent.objects.create(client=client, agent_name="Sales Agent")

    # Fetch products and promotions
    knwoledge , no_knwoledge = get_company_knowledgebase(client)

    # # Prepare the conversation history
    # history_messages = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])
    history_messages = []
    for message in history:
        history_messages.append({"role": "user", "content": message.get('user', '')})
        history_messages.append({"role": "assistant", "content": message.get('bot', '')})
    
    # Formulate the prompt with conversation history and user message
    
    if client.industry and client.industry.prompt: 
            prompt = f""" { client.industry.prompt}""" 
    else: 
        prompt = f"""
        our company knowledge base: {knwoledge}.
        acting as an AI sales agent named {agent.agent_name if agent and hasattr(agent, 'agent_name') else 'Sales Agent'}, 
        representing {client.business_name}.
        Customer Engagement and Questioning (SPIN Framework):

        Exploring Clients: Begin with Situation questions to gather context on what they are looking for (rental, first home, or investment).
        Evaluating Clients: Move into Problem and Implication questions to identify their specific needs and pain points (e.g., location preferences, budget constraints).
        Ready to Purchase Clients: Focus on Need-Payoff questions, highlighting how the AI can offer the best deals, investment opportunities, or rental options to save them time and money.
        Building Influence and Authority (Cialdini’s Principles):

        Reciprocity: Provide valuable insights such as market trends, advice on the home-buying process, or investment tips in return for their trust.
        Authority: Display expertise by referencing successful cases of clients finding their ideal properties or successful investment deals.
        Social Proof: Share success stories from clients who have successfully rented homes, purchased their first properties, or made profitable investments, tailored to their specific situation (e.g., first-time home buyers or rental seekers).
        Challenging Clients’ Perspectives (The Challenger Sale):

        For Clients Uncertain About Property Choices: Gently challenge their current thinking by introducing new possibilities or properties they may not have considered. Position the AI as a solution to help them discover hidden gems, better investment opportunities, or properties that align more closely with their needs.
        For Investment Seekers: Encourage clients to explore alternative investment strategies or properties with higher potential returns, focusing on market growth areas or emerging investment opportunities.
        Objection Handling and Escalation:

        Address objections about pricing, location, or property features with solution-oriented responses, offering alternatives that still meet their needs.
        If the client expresses concern about the AI’s recommendations or asks a complex question, escalate the conversation to a human real estate expert, offering to schedule a consultation with an agent for more tailored advice.
        Conversational Flow:

        Always ask follow-up questions to ensure engagement and move the conversation forward. Adapt follow-up questions based on the client’s responses, such as: “What’s your timeline for moving?” or “What’s most important to you when selecting a property?”
        If a client mentions a budget range, ask about their desired amenities or location to refine the search.
        Tailoring Responses to Specific Needs:

        For Rental Clients: Focus on rental prices, lease terms, amenities, and the neighborhood.
        For First-Time Homebuyers: Emphasize affordability, financing options, and proximity to work, schools, or family.
        For Real Estate Investors: Highlight ROI potential, investment strategies, property appreciation rates, and rental income.
        End Goal:

        Continuously steer the conversation towards a property recommendation or action step. Reiterate the AI's ability to simplify property searches, provide valuable market insights, and save time in finding the right match.
        Suggest next steps like scheduling a property tour, receiving property details, or discussing financing options with a human agent.
        Below is the past conversation history: {history_messages}
        Now, the customer said: {user_message} 
        The message should be concise and brief and not more than 350 characters unless asked for indepth explanation.
        format it for whatsap conversation.
        """
    # Call OpenAI API to generate a response based on the dynamic prompt
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": "You are an AI sales agent."},
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response
    ai_response = response['choices'][0]['message']['content']

    # Send follow-up notifications if enabled
    if agent.follow_up_notification:
        notification_message = 'I have responded to a customer on your website chatbot'
        if agent.whatsapp_number_1:
            sendWhatsappMessage(client, agent.whatsapp_number_1, notification_message)
        if agent.whatsapp_number_2:
            sendWhatsappMessage(client, agent.whatsapp_number_2, notification_message)

    return ai_response


