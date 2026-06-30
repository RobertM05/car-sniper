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
            """,
        }

        email = resend.Emails.send(params)
        print(f"Alert email sent successfully! ID: {email['id']}")
        return True

    except Exception as e:
        print(f"Failed to send email via Resend: {str(e)}")
        return False


def send_contact_email(
    name: str,
    phone: str,
    company_email: str,
    company_name: str,
    has_website: str,
    website_ip: str | None = None,
):
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
                        {f'<li style="margin-bottom: 15px;"><strong>Website IP:</strong> {website_ip}</li>' if has_website == "Da" and website_ip else ""}
                    </ul>
                </div>
                
                <p style="font-size: 12px; color: #a1a1aa; text-align: center; margin-top: 30px; border-top: 1px solid #27272a; padding-top: 20px;">
                    CarSniper B2B Dashboard
                </p>
            </div>
            """,
        }

        email = resend.Emails.send(params)
        print(f"Contact lead successfully sent to admin! ID: {email['id']}")
        return True

    except Exception as e:
        print(f"Failed to send contact lead email: {str(e)}")
        return False


def send_new_cars_email(user_email: str, make: str, model: str, cars: list):
    """
    Sends a beautiful HTML email to the user with the new matched cars from the background cron job.
    """
    resend.api_key = os.environ.get("RESEND_API_KEY", "")

    if not resend.api_key:
        print("Warning: RESEND_API_KEY is not set. Cannot send new cars email.")
        return False

    try:
        cars_html = ""
        for car in cars:
            price_display = f"{car.get('price', 'N/A')} EUR"
            km_display = f"{car.get('km', 'N/A')} km"
            year_display = f"{car.get('year', 'N/A')}"
            link = car.get("link", "#")
            image = car.get("image", "https://via.placeholder.com/150?text=No+Image")

            cars_html += f"""
            <div style="background-color: #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #333;">
                <img src="{image}" alt="Car" style="width: 100%; height: 150px; object-fit: cover; border-radius: 5px;">
                <div style="margin-top: 15px;">
                    <h3 style="margin: 0 0 10px 0; color: #ffffff;"><a href="{link}" style="color: #ffffff; text-decoration: none;">{car.get("title", "Vehicul Nou")}</a></h3>
                    <p style="margin: 0 0 5px 0; color: #4ade80; font-weight: bold; font-size: 18px;">{price_display}</p>
                    <p style="margin: 0; color: #a1a1aa; font-size: 14px;">An: {year_display} • Rulaj: {km_display} • {car.get("city", "N/A")}</p>
                    <a href="{link}" style="display: block; text-align: center; margin-top: 15px; background-color: #38bdf8; color: #000; padding: 10px 16px; border-radius: 4px; text-decoration: none; font-weight: bold; font-size: 14px;">Vezi Anunțul</a>
                </div>
            </div>
            """

        params = {
            "from": "CarSniper Alerts <onboarding@resend.dev>",
            "to": [user_email],
            "subject": f"🔥 {make} {model}: {len(cars)} Anunțuri Recente!",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #0a0a0a; color: #ffffff; border-radius: 10px;">
                <h2 style="color: #38bdf8; text-align: center;">Am găsit oferte noi!</h2>
                
                <p style="font-size: 16px; line-height: 1.5; text-align: center;">Sniperul nostru a identificat <strong style="color: #4ade80;">{len(cars)}</strong> mașini complet noi apărute în ultima perioadă care corespund filtrului tău pentru <strong>{make} {model}</strong>.</p>
                
                <div style="margin: 30px 0;">
                    {cars_html}
                </div>
                
                <p style="font-size: 12px; color: #a1a1aa; text-align: center; margin-top: 30px; border-top: 1px solid #27272a; padding-top: 20px;">
                    © {make.title()} CarSniper Alerts
                </p>
            </div>
            """,
        }

        email = resend.Emails.send(params)
        print(f"Cron alert email successfully sent to {user_email}! ID: {email['id']}")
        return True

    except Exception as e:
        print(f"Failed to send cron alert email: {str(e)}")
        return False
