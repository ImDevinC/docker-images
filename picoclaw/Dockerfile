# Docker command:
#   docker run -d -v ~/.picoclaw:/home/picoclaw/.picoclaw -p 8080:8080 imdevinc/picoclaw

FROM golang:1.25-alpine AS builder

LABEL maintainer="Devin Collins <me@imdevinc.com>"

# Install build dependencies
RUN apk add --no-cache \
    git \
    make \
    gcc \
    musl-dev

WORKDIR /build

# Clone the repository
RUN git clone https://github.com/sipeed/picoclaw.git .

# Build the application
RUN make deps && \
    make build

# Final stage
FROM alpine:latest

LABEL maintainer="Devin Collins <me@imdevinc.com>"

WORKDIR /app

# Copy binary from builder
COPY --from=builder --chmod=755 /build/build/picoclaw-linux-amd64 /app/picoclaw

# Install runtime dependencies
RUN apk add --no-cache \
    ca-certificates \
    && adduser -D -s /bin/sh picoclaw \
    && mkdir -p /home/picoclaw/.picoclaw \
    && chown -R picoclaw:picoclaw /app /home/picoclaw/.picoclaw

USER picoclaw

# Default command runs the gateway
ENTRYPOINT ["/app/picoclaw"]
CMD ["gateway"]
