import os
import resend
from dotenv import load_dotenv

load_dotenv()

def send_alert_email(user_email: str, make: str, model: str, max_price: int):
    """
    Sends an email to the user confirming their alert has been set up.
    This uses the Resend REST API which is extremely fast and Vercel-friendly.
    """
    
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    
    if not resend.api_key:
        print("Warning: RESEND_API_KEY is not set in environment variables.")
        return False
        
    try:
        params = {
            "from": "CarSniper Alerts <onboarding@resend.dev>",
            "to": [user_email],
            "subject": f"Alerta Activata: {make} {model}",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #0a0a0a; color: #ffffff; border-radius: 10px;">
                <h2 style="color: #38bdf8; text-align: center;">Alerta CarSniper Activata!</h2>
                
                <p style="font-size: 16px; line-height: 1.5;">Salut,</p>
                <p style="font-size: 16px; line-height: 1.5;">Am înregistrat alerta ta. Te vom notifica imediat ce găsim oferte noi care corespund criteriilor tale:</p>
                
                <div style="background-color: #121212; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #38bdf8;">
                    <ul style="list-style-type: none; padding: 0; margin: 0; font-size: 16px;">
                        <li style="margin-bottom: 10px;"><strong>Marca:</strong> {make}</li>
                        <li style="margin-bottom: 10px;"><strong>Model:</strong> {model}</li>
                        <li><strong>Pret Maxim:</strong> {max_price} EUR</li>
                    </ul>
                </div>
                
                <p style="font-size: 14px; color: #a1a1aa; text-align: center; margin-top: 30px;">
                    © 2024 CarSniper. Aceasta este o platformă SaaS demo.
                </p>
            </div>
            """
        }

        email = resend.Emails.send(params)
        print(f"Alert email sent successfully! ID: {email['id']}")
        return True
        
    except Exception as e:
        print(f"Failed to send email via Resend: {str(e)}")
        return False

def send_contact_email(name: str, phone: str, company_email: str, company_name: str, has_website: str, website_ip: str | None = None):
    """
    Sends a 'Devino Partener' lead email to the platform administrator.
    """
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    
    if not resend.api_key:
        print("Warning: RESEND_API_KEY is not set. Cannot send contact email.")
        return False
        
    try:
        params = {
            "from": "CarSniper Leads <onboarding@resend.dev>",
            "to": ["robert.musoiu05@gmail.com"],
            "subject": f"Lead Nou Partener: {company_name}",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #0a0a0a; color: #ffffff; border-radius: 10px;">
                <h2 style="color: #4ade80; text-align: center;">Solicitare Noua: Devino Partener</h2>
                
                <p style="font-size: 16px; line-height: 1.5; text-align: center;">Ai primit o noua cerere de la un dealer auto care doreste sa intre in reteaua CarSniper.</p>
                
                <div style="background-color: #121212; padding: 20px; border-radius: 8px; margin: 30px 0; border: 1px solid #4ade80;">
                    <ul style="list-style-type: none; padding: 0; margin: 0; font-size: 16px;">
                        <li style="margin-bottom: 15px;"><strong>Nume Contact:</strong> {name}</li>
                        <li style="margin-bottom: 15px;"><strong>Companie:</strong> {company_name}</li>
                        <li style="margin-bottom: 15px;"><strong>Email Firma:</strong> <a href="mailto:{company_email}" style="color: #38bdf8;">{company_email}</a></li>
                        <li style="margin-bottom: 15px;"><strong>Telefon:</strong> <a href="tel:{phone}" style="color: #38bdf8;">{phone}</a></li>
                        <li style="margin-bottom: 15px;"><strong>Are Website?</strong> {has_website}</li>
                        {f'<li style="margin-bottom: 15px;"><strong>Website IP:</strong> {website_ip}</li>' if has_website == 'Da' and website_ip else ''}
                    </ul>
                </div>
                
                <p style="font-size: 12px; color: #a1a1aa; text-align: center; margin-top: 30px; border-top: 1px solid #27272a; padding-top: 20px;">
                    CarSniper B2B Dashboard
                </p>
            </div>
            """
        }

        email = resend.Emails.send(params)
        print(f"Contact lead successfully sent to admin! ID: {email['id']}")
        return True
        
    except Exception as e:
        print(f"Failed to send contact lead email: {str(e)}")
        return False
