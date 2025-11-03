"""
ElevenLabs Voice Cloning Integration
Handles voice cloning and audio generation using ElevenLabs API
"""
import os
import requests
from typing import Optional, Dict
import base64

class VoiceCloneManager:
    """Manage voice cloning with ElevenLabs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with ElevenLabs API key"""
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set. Please set it to use voice cloning features.")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key
        }
    
    def create_voice_clone(self, 
                          voice_name: str, 
                          audio_file_path: str,
                          description: Optional[str] = None) -> Optional[str]:
        """
        Create a voice clone from an audio sample
        
        Args:
            voice_name: Name for the voice clone
            audio_file_path: Path to audio sample file (30-60 seconds)
            description: Optional description of the voice
            
        Returns:
            voice_id if successful, None if failed
        """
        try:
            # Read audio file
            with open(audio_file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            
            # Prepare files for upload
            files = {
                'files': ('sample.mp3', audio_data, 'audio/mpeg')
            }
            
            data = {
                'name': voice_name,
                'description': description or f"Voice clone for {voice_name}"
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/voices/add",
                headers=self.headers,
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                voice_id = result.get('voice_id')
                print(f"✓ Voice clone created successfully: {voice_id}")
                return voice_id
            else:
                print(f"✗ Error creating voice clone: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except FileNotFoundError:
            print(f"✗ Audio file not found: {audio_file_path}")
            return None
        except Exception as e:
            print(f"✗ Error creating voice clone: {e}")
            return None
    
    def get_voice_details(self, voice_id: str) -> Optional[Dict]:
        """
        Get details about a voice
        
        Args:
            voice_id: The voice ID
            
        Returns:
            Dictionary with voice details or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices/{voice_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Error getting voice details: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting voice details: {e}")
            return None
    
    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a voice clone
        
        Args:
            voice_id: The voice ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/voices/{voice_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                print(f"✓ Voice deleted successfully: {voice_id}")
                return True
            else:
                print(f"✗ Error deleting voice: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error deleting voice: {e}")
            return False
    
    def list_voices(self) -> Optional[list]:
        """
        List all available voices (including clones)
        
        Returns:
            List of voice dictionaries or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('voices', [])
            else:
                print(f"✗ Error listing voices: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Error listing voices: {e}")
            return None

class AudioGenerator:
    """Generate audio from text using ElevenLabs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with ElevenLabs API key"""
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set. Please set it to use audio generation features.")
        
        self.base_url = "https://api.elevenlabs.io/v1"
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def generate_audio(self,
                      text: str,
                      voice_id: str,
                      output_path: str,
                      model_id: str = "eleven_monolingual_v1",
                      stability: float = 0.5,
                      similarity_boost: float = 0.75) -> bool:
        """
        Generate audio from text using a voice
        
        Args:
            text: The text to convert to speech
            voice_id: The voice ID to use
            output_path: Where to save the audio file
            model_id: ElevenLabs model to use
            stability: Voice stability (0-1)
            similarity_boost: Voice similarity boost (0-1)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare request data
            data = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost
                }
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=self.headers,
                json=data,
                stream=True
            )
            
            if response.status_code == 200:
                # Save audio to file
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f"✓ Audio generated successfully: {output_path}")
                return True
            else:
                print(f"✗ Error generating audio: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error generating audio: {e}")
            return False
    
    def get_character_count(self, voice_id: str) -> Optional[Dict]:
        """
        Get character usage information for the API key
        
        Returns:
            Dictionary with character count info or None
        """
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers={"xi-api-key": self.api_key}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Error getting character count: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"✗ Error getting character count: {e}")
            return None

def create_voice_from_sample(sample_path: str, voice_name: str, user_id: int) -> Optional[str]:
    """
    Convenience function to create a voice clone
    
    Args:
        sample_path: Path to audio sample
        voice_name: Name for the voice
        user_id: User ID (for description)
        
    Returns:
        voice_id if successful, None otherwise
    """
    try:
        manager = VoiceCloneManager()
        voice_id = manager.create_voice_clone(
            voice_name=f"{voice_name}_user{user_id}",
            audio_file_path=sample_path,
            description=f"Voice clone for user {user_id}"
        )
        return voice_id
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error creating voice clone: {e}")
        return None

def generate_voice_audio(text: str, voice_id: str, output_path: str) -> bool:
    """
    Convenience function to generate audio
    
    Args:
        text: Text to convert to speech
        voice_id: Voice ID to use
        output_path: Where to save audio
        
    Returns:
        True if successful, False otherwise
    """
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, voice_id, output_path)
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error generating audio: {e}")
        return False

if __name__ == "__main__":
    # Test voice cloning functionality
    print("Testing ElevenLabs Voice Clone integration...")
    
    # Check if API key is set
    if not os.getenv('ELEVENLABS_API_KEY'):
        print("⚠ ELEVENLABS_API_KEY not set. Cannot test.")
    else:
        print("✓ API key found")
        
        # Test listing voices
        manager = VoiceCloneManager()
        voices = manager.list_voices()
        if voices:
            print(f"✓ Found {len(voices)} voices available")
        else:
            print("✗ Could not list voices")
