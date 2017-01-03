from twilio.rest import TwilioRestClient
import phonenumbers

account_sid   = ""
auth_token    = ""
sender_number = ""

def convert_to_e164(raw_phone):
    if not raw_phone:
        return
    if raw_phone[0] == '+':
        # Phone number may already be in E.164 format.
        parse_type = None
    else:
        # If no country code information present, assume it's a US number
        parse_type = "US"
    phone_representation = phonenumbers.parse(raw_phone, parse_type)
    return phonenumbers.format_number(phone_representation, phonenumbers.PhoneNumberFormat.E164)

def send_sms(to, body):
    if len(account_sid) == 0 or len(auth_token) == 0 or len(sender_number) == 0:
        return
    to = convert_to_e164(to)
    client = TwilioRestClient(account_sid, auth_token)
    message = client.messages.create(body=body,
        to=to,
        from_=sender_number)
    return
