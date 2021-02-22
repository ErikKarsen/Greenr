import boto3
import base64
from os import getenv

#DJANGO SECRETS
SECRET_KEY = 'AQICAHjNFeZuqPl8K37ILC2+U1n7RRy5mVWwGjhe9xZq7wEJaQE+Fx5fo4DEQs+WyQkdBHXMAAAAkjCBjwYJKoZIhvcNAQcGoIGBMH8CAQAwegYJKoZIhvcNAQcBMB4GCWCGSAFlAwQBLjARBAyDf/undVGWvMrXXHICARCATWkHh14mMl0ZcJjxBxWjlE0krhcdLtEAPLuAhNVYvbO2R1zF6DG2GeVW+4ecjAM523/9oOeoJl+JbyK5OVsFrj/koXqxKvR63DlgihQC'

#GMAIL USER SECRETS
EMAIL_HOST_USER = 'finalprojectgreenr@gmail.com'
EMAIL_HOST_PASSWORD = 'AQICAHjNFeZuqPl8K37ILC2+U1n7RRy5mVWwGjhe9xZq7wEJaQHbv/uF+AG2wSuoGAGveu4rAAAAbjBsBgkqhkiG9w0BBwagXzBdAgEAMFgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMLFUG9Ame5zJQhXuXAgEQgCvP3j2S2NQti+F+xYKIuDULAMHJ1njVRf9UQwoGXrNdV09Jx3mqboj6Hvsg'

#DB USER SECRETS
DB_NAME = 'greenr_1'
DB_USER = 'erik1'
DB_PASSWORD = 'AQICAHjNFeZuqPl8K37ILC2+U1n7RRy5mVWwGjhe9xZq7wEJaQFoD9vtz0yIEZrJsrLBcjanAAAAbjBsBgkqhkiG9w0BBwagXzBdAgEAMFgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMBEMP7M9IBfgx+eUKAgEQgCu/8hm96Dol+/LipS1cVux8x0oJcYMzuFjJbu9UKHiryZxGXBDrXGpqwfhs'
DB_HOST = 'database-1.crvi4vvqrbu8.eu-west-2.rds.amazonaws.com'

#AWS SECRETS
AWS_ACCESS_KEY_ID = 'AQICAHjNFeZuqPl8K37ILC2+U1n7RRy5mVWwGjhe9xZq7wEJaQHGWjPUuuHf1aT67L1WDumjAAAAcjBwBgkqhkiG9w0BBwagYzBhAgEAMFwGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQM5loH5TrVRovaeI36AgEQgC/jA3/omv3uDzE0hqHWl47Fje5NkY84grkzrS4enYJQ2SORrJyqS3XgecEp87iyNw=='
AWS_SECRET_ACCESS_KEY = 'AQICAHjNFeZuqPl8K37ILC2+U1n7RRy5mVWwGjhe9xZq7wEJaQFiY7VDgKL1+2J1P5dMk3XXAAAAhzCBhAYJKoZIhvcNAQcGoHcwdQIBADBwBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDAqC5qq6FgzV60j7MgIBEIBDS3VywKuEIIUEEQpjozAGYTKDqTu7mWJzyRp1V6x1XENWikPClADYwlk4oOBe8bu3i/UqK2JuUf9JGM77DfwjFnshCQ=='
AWS_STORAGE_BUCKET_NAME = 'project-greenr-bucket'


boto_kwargs = {
    "aws_access_key_id": getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": getenv("AWS_SECRET_ACCESS_KEY"),
    "profile_name": "projectgreenr"
}


def decrypt(secret, **boto_kwargs):
    client = boto3.Session(**boto_kwargs).client("kms",  region_name='eu-west-2')

    plaintext = client.decrypt(
        CiphertextBlob=bytes(base64.b64decode(secret))
    )
    return plaintext["Plaintext"].decode('utf-8')


SECRET_KEY = decrypt(SECRET_KEY)
EMAIL_HOST_PASSWORD = decrypt(EMAIL_HOST_PASSWORD)
DB_PASSWORD = decrypt(DB_PASSWORD)
AWS_ACCESS_KEY_ID = decrypt(AWS_ACCESS_KEY_ID)
AWS_SECRET_ACCESS_KEY = decrypt(AWS_SECRET_ACCESS_KEY)