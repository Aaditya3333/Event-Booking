# Placeholder Dockerfile for Render
# This allows Render to clone the repository successfully
# The actual deployment will use manual setup

FROM alpine:latest
LABEL maintainer="Event Booking System"
CMD ["echo", "Repository cloned successfully - use manual setup"]
