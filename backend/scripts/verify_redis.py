import redis
import os
import sys
from celery import Celery

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

def verify_redis_connection():
    print(f"1. Checking raw Redis connection at {settings.REDIS_SERVER}:{settings.REDIS_PORT}...")
    try:
        r = redis.Redis(host=settings.REDIS_SERVER, port=settings.REDIS_PORT, db=0, socket_timeout=3)
        ping_result = r.ping()
        print(f"   -> Success! Redis PING returned: {ping_result}")
    except Exception as e:
        print(f"   -> FAILED to connect to Redis: {e}")
        return False
    return True

def verify_celery_connection():
    print("2. Checking Celery broker connection...")
    try:
        broker_url = f"redis://{settings.REDIS_SERVER}:{settings.REDIS_PORT}/0"
        app = Celery('veridex', broker=broker_url)
        
        # This will raise an exception if it can't connect to the broker
        with app.connection_for_write() as conn:
            conn.default_channel.basic_publish(
                "ping", 
                exchange="", 
                routing_key="test_queue", 
                body="test",
                properties={}
            )
        print("   -> Success! Celery can connect and publish to the Redis broker.")
        return True
    except Exception as e:
        print(f"   -> FAILED: Celery broker connection issue: {e}")
        return False

if __name__ == "__main__":
    redis_ok = verify_redis_connection()
    celery_ok = verify_celery_connection()
    
    if redis_ok and celery_ok:
        print("\nSUCCESS: Redis and Celery infrastructure are fully validated and real!")
    else:
        print("\nFAILED: Redis verification failed. Make sure 'docker-compose up -d' is running.")
