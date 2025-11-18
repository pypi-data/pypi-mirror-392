"""
Utility functions for WhatsApp audio message handling.
"""

import glob
import json
import logging
import os
import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import Response
import requests
#from pydub import AudioSegment



logger = logging.getLogger(__name__)



class WhatsAppError(Exception):
    """Custom exception for WhatsApp API errors."""
    pass


class AudioConversionError(Exception):
    """Custom exception for audio conversion errors."""
    pass

def webhook_check(challenge,token,VERIFY_TOKEN):
    print(f"{challenge},{token},{VERIFY_TOKEN}")
    if token == VERIFY_TOKEN:
        print(f"{challenge},{token},{VERIFY_TOKEN}")
        logger.info("Webhook verified successfully")
        return Response(content=challenge, status_code=status.HTTP_200_OK)
    else:
        logger.warning("Webhook verification failed: invalid token or missing challenge")
        return Response(content="Verification failed", status_code=status.HTTP_403_FORBIDDEN)
    
def get_message(data):
    try:
        logger.info("Incoming webhook payload: %s", json.dumps(data, indent=2, ensure_ascii=False))

        entry = data.get("entry", [])[0].get("changes", [])[0].get("value", {})
        messages = entry.get("messages", [])

        if not messages:
            logger.info("No messages found in webhook payload")
            return {"res":True,"msg":""}

        msg = messages[0]
        return {"res":True,
                "msg":msg}

    except Exception as e:
        logger.error("Error in delete_files_by_mask: %s", str(e))
        return {"res":False}


def delete_files_by_mask(directory: str, pattern: str) -> int:
    """
    Delete files in a directory matching a given pattern.
    
    Args:
        directory: Directory to search in
        pattern: File pattern (e.g., '*.mp3', 'temp_*')
        
    Returns:
        Number of files deleted
    """
    try:
        files = glob.glob(os.path.join(directory, pattern))
        deleted_count = 0

        for file_path in files:
            try:
                os.remove(file_path)
                deleted_count += 1
                logger.info("Deleted file: %s", file_path)
            except Exception as e:
                logger.warning("Failed to delete %s: %s", file_path, str(e))

        logger.info("Total files deleted: %d", deleted_count)
        return deleted_count
        
    except Exception as e:
        logger.error("Error in delete_files_by_mask: %s", str(e))
        return 0



def send_whatsapp_text_message(to: str, message: str, sys_conf: dict) -> Dict[str, Any]:
    """
    Send WhatsApp text message via Meta Graph API.
    
    Args:
        to: Recipient phone number
        message: Text message to send
        sys_conf: System configuration dictionary
        
    Returns:
        API response
        
    Raises:
        WhatsAppError: If message sending fails
    """
    try:
        url = f"https://graph.facebook.com/v22.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
        headers = {
            "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Text message sent successfully to %s", to)
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send WhatsApp text message: %s", str(e))
        raise WhatsAppError(f"Failed to send text message: {str(e)}") from e


def whatsapp_upload_media(file_path: str, sys_conf: dict) -> Optional[str]:
    """
    Upload media file to WhatsApp and return media ID.
    
    Args:
        file_path: Path to media file
        sys_conf: System configuration dictionary
        
    Returns:
        Media ID if successful, None otherwise
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Media file not found: {file_path}")

        url = f"https://graph.facebook.com/v20.0/{sys_conf['PHONE_NUMBER_ID']}/media"
        headers = {"Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}"}

        with open(file_path, "rb") as file:
            files = {"file": (os.path.basename(file_path), file, "audio/mpeg")}
            data = {"messaging_product": "whatsapp"}
            response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
            response.raise_for_status()

        result = response.json()
        logger.info("Media uploaded successfully: %s", result.get("id"))
        return result.get("id")
        
    except Exception as e:
        logger.error("Failed to upload media to WhatsApp: %s", str(e))
        return None


def send_whatsapp_audio_by_id(to: str, media_id: str, sys_conf: dict) -> Dict[str, Any]:
    """
    Send WhatsApp audio message using media ID.
    
    Args:
        to: Recipient phone number
        media_id: WhatsApp media ID
        sys_conf: System configuration dictionary
        
    Returns:
        API response
        
    Raises:
        WhatsAppError: If audio sending fails
    """
    try:
        url = f"https://graph.facebook.com/v20.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
        headers = {
            "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": {"id": media_id}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Audio message sent successfully to %s", to)
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send WhatsApp audio message: %s", str(e))
        raise WhatsAppError(f"Failed to send audio message: {str(e)}") from e


def send_whatsapp_voice(to, ogg_path,sys_conf):
    url = f"https://graph.facebook.com/v21.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}"
    }
    files = {
        "file": (os.path.basename(ogg_path), open(ogg_path, "rb"), "audio/ogg; codecs=opus")
    }
    data = {
        "messaging_product": "whatsapp"  # ✅ REQUIRED HERE
    }

    # Step 1: upload media
    upload_resp = requests.post(
        f"https://graph.facebook.com/v21.0/{sys_conf['PHONE_NUMBER_ID']}/media",
        headers=headers,
        files=files,
        data=data
    ).json()
    logger.info(f"##  upload_resp  {upload_resp} " )

    media_id = upload_resp["id"]

    # Step 2: send voice message
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {
            "id": media_id
        }
    }
    resp = requests.post(url, headers=headers, json=data)
    return resp.json()

def send_globy_text_message_t(to,respons,sys_conf):
    #"text": f"""{respons['answer']} 
    #                        {respons['documents'][0]}"""
    logger.info(f"""### WhatsAppOutput_msg globy
                {respons}
                
                """)
    try:
        url = f"https://graph.facebook.com/v23.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
        headers = {
            "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": f"{respons['answer']} www.google.com "}
        }

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        logger.info("Text message sent successfully to %s", to)
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error("Failed to send WhatsApp text message: %s", str(e))
        raise WhatsAppError(f"Failed to send text message: {str(e)}") from e


def send_custome_text_message(to,text,sys_conf,agent,thread="",t_list=[],b_list=[]):
    logger.info("### WhatsAppOutput_msg - send_indus_selc ###")
    
    qt=""
    bl=[]
    for n,i in enumerate(b_list):
        t_list=" \n".join(t_list)
        
        if n<3:
            qt=qt+f"""\n{n+1}) {i}"""
            bl.append({"type": "reply",
                            "reply": {
                                "id": i,
                                "title": str(n)
                            }})
    url = f"https://graph.facebook.com/v22.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}", 
        "Content-Type": "application/json"
    }
    logger.info(f""" tespons 
                
                {text}

                {t_list}

                {bl}


                """)
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": text+qt
            },
            "action": {
                "buttons": bl
            }
        }
    }
    
    logger.info(f"""

            {payload}

        """)
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code != 200:
            print(f"Error details: {r.json()}")
        else:
            print("Message sent successfully!")
            
    except Exception as e:
        print(f"Request failed: {e}")

    return {"status":r.status_code,"res":r.json()}


def send_globy_text_message_t_1(text,sys_conf):
    logger.info("### WhatsAppOutput_msg - send_indus_selc ###")
    
    url = f"https://graph.facebook.com/v20.0/{sys_conf['PHONE_NUMBER_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {sys_conf['WHATSAPP_TOKEN']}", 
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": "201090370389",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": text
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "بيبرب ",
                            "title": "ثبيثب"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "بطاقة_الهوية", 
                            "title": "بطاقة الهوية"
                        }
                    },
                    {
                        "type": "reply", 
                        "reply": {
                            "id": "مستندات_المعاينة",
                            "title": "مستندات المعاينة"
                        }
                    }
                    
                ]
            }
        }
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code != 200:
            print(f"Error details: {r.json()}")
        else:
            print("Quick reply buttons sent successfully!")
            
    except Exception as e:
        print(f"Request failed: {e}")