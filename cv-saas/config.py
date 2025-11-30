import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cv_saas_super_secret_key_2024_123!'
    STRIPE_PUBLIC_KEY = 'pk_test_51SWdoHRbTGOIXLwnCTYoc2Aq3pkySs2rFBcXQNcqt8Ey5hsEjESFvfPElz1b5vF8GgWYUZTZ3ZT2AoXKPqAES0TF00M3ZAvVEz'
    STRIPE_SECRET_KEY = 'sk_test_51SWdoHRbTGOIXLwnhFbcbVgHdZzgsIKsWz0tvdCxfH30qXy7mr7DBIZKcwGSOaavQAMx6BQbh5wKVlXIJvRNrb1n00wkqkv6mD'