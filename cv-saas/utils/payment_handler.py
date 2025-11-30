import stripe

# Configuration directe
STRIPE_SECRET_KEY = 'sk_test_51SWdoHRbTGOIXLwnhFbcbVgHdZzgsIKsWz0tvdCxfH30qXy7mr7DBIZKcwGSOaavQAMx6BQbh5wKVlXIJvRNrb1n00wkqkv6mD'

stripe.api_key = STRIPE_SECRET_KEY


def create_checkout_session(subscription_type='monthly'):
    try:
        if subscription_type == 'yearly':
            # Abonnement annuel - 799 MAD
            unit_amount = 79900
            product_name = 'Abonnement Annuel Premium AI CV Reviewer'
            description = 'Analyses illimitées de CV pendant 1 an'
        else:
            # Abonnement mensuel - 99 MAD
            unit_amount = 9900
            product_name = 'Abonnement Mensuel Premium AI CV Reviewer'
            description = 'Analyses illimitées de CV pendant 1 mois'

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'mad',
                    'product_data': {
                        'name': product_name,
                        'description': description
                    },
                    'unit_amount': unit_amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:5000/success?type={subscription_type}&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url='http://localhost:5000/subscription',
        )
        return session
    except Exception as e:
        print(f"Erreur Stripe: {e}")
        raise e