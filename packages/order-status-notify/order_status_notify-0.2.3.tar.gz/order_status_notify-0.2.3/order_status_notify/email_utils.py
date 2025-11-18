def notify_status_change(user, order):
    try:
        # Lazy imports inside the function
        from django.core.mail import EmailMultiAlternatives
        from django.template.loader import render_to_string
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)
        
        context = {
            'username': user.username,
            'order_id': order.id,
            'status': order.status,
            'site_name': 'Italians by the Bay',
        }

        html_content = render_to_string('emails/order_status_update.html', context)
        subject = f"Order #{order.id} Status Update"
        body = f"Your order #{order.id} status has been updated to: {order.status}"

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        logger.info(f"Email sent to {user.email} for Order #{order.id}")


    except Exception as e:
        logger.error(f"Failed to send email for Order #{order.id}: {e}")
