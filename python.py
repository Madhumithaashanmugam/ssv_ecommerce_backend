import secrets

# For Vendor
vendor_secret = secrets.token_urlsafe(32)
print("Vendor Secret Key:", vendor_secret)

# For Customer
customer_secret = secrets.token_urlsafe(32)
print("Customer Secret Key:", customer_secret)
