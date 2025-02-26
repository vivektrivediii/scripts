#!/bin/bash

# Variables
HOSTED_ZONE_ID="Z0561180VWH3WDP281OB123"  # Replace with your Route 53 Hosted Zone ID
NEW_LB_DNS="a3b123f6a7285e9d4bd1a2a36789f1e0cd4-1966422859.us-east-1.elb.amazonaws.com"  # Load Balancer DNS
AWS_REGION="us-east-1"  # Update with your AWS region

# Fetch ELB Hosted Zone ID dynamically
ELB_HOSTED_ZONE_ID=$(aws elb describe-load-balancers --query "LoadBalancerDescriptions[?DNSName=='$NEW_LB_DNS'].CanonicalHostedZoneNameID" --output text)

if [ -z "$ELB_HOSTED_ZONE_ID" ]; then
    echo "Error: Could not fetch ELB Hosted Zone ID for $NEW_LB_DNS"
    exit 1
fi

# Domains to update
DOMAINS=("app.test.ai" "app2.test.ai")

# Loop through the domains and update their records
for DOMAIN in "${DOMAINS[@]}"; do
    echo "Updating A record (Alias) for $DOMAIN to point to Load Balancer: $NEW_LB_DNS"

    # Create a JSON payload for updating the Route 53 Alias record
    cat > change-record.json <<EOF
    {
      "Comment": "Update Alias record to new Load Balancer",
      "Changes": [
        {
          "Action": "UPSERT",
          "ResourceRecordSet": {
            "Name": "$DOMAIN",
            "Type": "A",
            "AliasTarget": {
              "HostedZoneId": "$ELB_HOSTED_ZONE_ID",
              "DNSName": "dualstack.$NEW_LB_DNS",
              "EvaluateTargetHealth": true
            }
          }
        }
      ]
    }
EOF

    # Update Route 53 record using AWS CLI
    aws route53 change-resource-record-sets --hosted-zone-id "$HOSTED_ZONE_ID" --change-batch file://change-record.json

    if [ $? -eq 0 ]; then
        echo "Successfully updated $DOMAIN to alias $NEW_LB_DNS"
    else
        echo "Failed to update $DOMAIN"
    fi

    # Cleanup JSON file
    rm -f change-record.json
done
