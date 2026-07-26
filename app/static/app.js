// DeployGuard Dynamic Health & Info Poller

document.addEventListener('DOMContentLoaded', () => {
    const POLL_INTERVAL_MS = 5000;

    async function fetchDeploymentState() {
        try {
            const response = await fetch('/api/info');
            if (!response.ok && response.status !== 503) {
                console.warn('Unexpected response status:', response.status);
                return;
            }

            const data = await response.json();
            updateUIState(data);
        } catch (error) {
            console.error('Failed to poll /api/info:', error);
        }
    }

    function updateUIState(data) {
        const isHealthy = data.health_status === 'healthy';

        // Update Top Header Status Badge
        const topBadge = document.getElementById('top-status-badge');
        const topText = document.getElementById('top-status-text');
        if (topBadge && topText) {
            topBadge.className = `status-badge ${isHealthy ? 'status-healthy' : 'status-unhealthy'}`;
            topText.textContent = isHealthy ? 'HEALTHY' : 'UNHEALTHY';
        }

        // Update Hero Status Text
        const heroStatus = document.getElementById('hero-status');
        if (heroStatus) {
            heroStatus.className = `metric-value ${isHealthy ? 'text-healthy' : 'text-unhealthy'}`;
            heroStatus.textContent = isHealthy ? 'HEALTHY' : 'UNHEALTHY';
        }

        // Update System Status Health Dot & Text
        const healthDot = document.getElementById('endpoint-health-dot');
        const healthText = document.getElementById('endpoint-health-text');
        if (healthDot && healthText) {
            healthDot.className = `status-item-indicator ${isHealthy ? 'status-dot-healthy' : 'status-dot-unhealthy'}`;
            healthText.className = `status-item-state ${isHealthy ? 'text-healthy' : 'text-unhealthy'}`;
            healthText.textContent = `● ${isHealthy ? 'Healthy' : 'Unhealthy (HTTP 503)'}`;
        }
    }

    // Initial check and periodic poller
    fetchDeploymentState();
    setInterval(fetchDeploymentState, POLL_INTERVAL_MS);
});
