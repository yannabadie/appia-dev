#!/bin/sh
# 🔧 Environment Variables Injection for GCP Cloud Run
# ====================================================

# Replace environment variables in built files
echo "🚀 Injecting runtime environment variables..."

# Backend URL from Cloud Run environment
if [ -n "$BACKEND_URL" ]; then
    echo "📡 Backend URL: $BACKEND_URL"
    # Replace placeholder in built files
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|__BACKEND_URL__|$BACKEND_URL|g" {} \;
fi

# Google Client ID from GCP Secret Manager
if [ -n "$GOOGLE_CLIENT_ID" ]; then
    echo "🔐 Google Client ID configured"
    find /usr/share/nginx/html -name "*.js" -exec sed -i "s|__GOOGLE_CLIENT_ID__|$GOOGLE_CLIENT_ID|g" {} \;
fi

# Environment detection
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏭 Production environment detected"
else
    echo "🧪 Development environment detected"
fi

echo "✅ Environment injection complete"
