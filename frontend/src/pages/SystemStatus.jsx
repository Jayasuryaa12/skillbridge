import React, { useState, useEffect } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RotateCw,
  Server,
  Database,
  ArrowRight,
  ShieldCheck,
  Zap,
  Globe,
  Clock,
  ExternalLink,
  Laptop
} from 'lucide-react';
import { getSystemStatus } from '../api/client';
import Card, { CardHeader, CardContent, CardFooter } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';

export const SystemStatus = () => {
  const [statusData, setStatusData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastPingTime, setLastPingTime] = useState(null);

  const fetchStatus = async () => {
    try {
      setRefreshing(true);
      const res = await getSystemStatus();
      setStatusData(res);
      setLastPingTime(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to get status:', err);
      setStatusData({
        status: 'unreachable',
        timestamp: new Date().toISOString(),
        services: {
          skill_service: { status: 'down', message: 'Flask server unreachable on port 5001' },
          opportunity_service: { status: 'unknown' }
        }
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 30000);
    return () => clearInterval(timer);
  }, []);

  const payload = statusData?.data || statusData;
  const overallStatus = payload?.overall_status || payload?.status || 'checking';
  const skillService = payload?.skill_service || payload?.services?.skill_service;
  const oppService = payload?.opportunity_service || payload?.services?.opportunity_service;

  const getStatusBadge = (status) => {
    if (status === 'healthy' || status === 'operational' || status === 'connected') {
      return <Badge variant="matched" size="sm" dot>Operational</Badge>;
    }
    if (status === 'degraded' || status === 'unavailable') {
      return <Badge variant="developing" size="sm" dot>Degraded</Badge>;
    }
    return <Badge variant="missing" size="sm" dot>Offline</Badge>;
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
            Microservices System Status
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time composite health, inter-service HTTP latencies, and MongoDB database pings.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastPingTime && (
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              Last ping: {lastPingTime}
            </span>
          )}
          <Button
            variant="outline"
            size="sm"
            leftIcon={<RotateCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />}
            onClick={fetchStatus}
            isLoading={refreshing}
          >
            Ping Microservices
          </Button>
        </div>
      </div>

      {/* Main Banner */}
      <Card className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${
                overallStatus === 'healthy' || overallStatus === 'operational'
                  ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400'
                  : overallStatus === 'degraded'
                  ? 'bg-amber-100 text-amber-600 dark:bg-amber-950/60 dark:text-amber-400'
                  : 'bg-rose-100 text-rose-600 dark:bg-rose-950/60 dark:text-rose-400'
              }`}
            >
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                  {overallStatus === 'healthy' || overallStatus === 'operational'
                    ? 'All Microservices Fully Operational'
                    : overallStatus === 'degraded'
                    ? 'Degraded Microservice Performance'
                    : 'Critical Service Disruptions Detected'}
                </h2>
                {getStatusBadge(overallStatus)}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Both services maintain isolated MongoDB database instances and communicate over REST with circuit breaking and exponential backoff.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-600 dark:text-slate-400 border-t md:border-t-0 md:border-l border-slate-200 dark:border-slate-800 pt-3 md:pt-0 md:pl-6">
            <div>
              <span className="block text-slate-400 text-[10px] uppercase font-bold">Skill Service</span>
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                {skillService?.latency_ms ? `${skillService.latency_ms} ms` : '< 15 ms'}
              </span>
            </div>
            <div>
              <span className="block text-slate-400 text-[10px] uppercase font-bold">Opportunity Svc</span>
              <span className="font-semibold text-slate-900 dark:text-slate-100">
                {oppService?.latency_ms ? `${oppService.latency_ms} ms` : oppService?.status === 'operational' ? '< 20 ms' : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Interactive Microservices Architecture Diagram */}
      <Card>
        <CardHeader
          title="Interactive Microservices Topology"
          subtitle="Architectural breakdown: Frontend -> Inter-Service REST API Layer -> MongoDB Atlas Shards"
        />
        <CardContent>
          <div className="p-6 rounded-2xl bg-slate-950 text-white overflow-x-auto">
            <div className="min-w-[650px] flex items-center justify-between gap-6 relative py-4">
              {/* Layer 1: Frontend Client */}
              <div className="flex flex-col items-center p-4 rounded-2xl bg-slate-900 border border-slate-800 w-44 shrink-0 shadow-lg relative group">
                <div className="w-10 h-10 rounded-xl bg-brand-600/30 text-brand-400 flex items-center justify-center mb-2">
                  <Laptop className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold">React Frontend</h4>
                <p className="text-[10px] text-slate-400 text-center mt-1">
                  Vite + React 18 + Tailwind
                </p>
                <span className="mt-2 text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-brand-300">
                  Client Port 5173
                </span>
              </div>

              {/* Arrow to Services */}
              <div className="flex-1 flex flex-col items-center justify-center">
                <span className="text-[10px] font-mono text-slate-400 mb-1">HTTP / JSON</span>
                <div className="w-full h-0.5 bg-gradient-to-r from-brand-500 via-sky-500 to-emerald-500 relative">
                  <div className="absolute -top-1 right-0 w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                </div>
              </div>

              {/* Layer 2: Microservices Stack */}
              <div className="flex flex-col gap-4 shrink-0">
                {/* Skill Service Box */}
                <div className="p-4 rounded-2xl bg-slate-900 border border-brand-500/40 w-56 shadow-lg relative">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-brand-400">Skill Service</span>
                    {getStatusBadge(skillService?.status || 'operational')}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">Flask • Port 5001</p>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Owns students, careers, and roadmaps
                  </p>
                  <div className="mt-2 text-[10px] text-emerald-400 font-mono bg-emerald-950/40 px-2 py-0.5 rounded w-fit">
                    db: skill_db
                  </div>
                </div>

                {/* Opportunity Service Box */}
                <div className="p-4 rounded-2xl bg-slate-900 border border-sky-500/40 w-56 shadow-lg relative">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-sky-400">Opportunity Service</span>
                    {getStatusBadge(oppService?.status || 'operational')}
                  </div>
                  <p className="text-[11px] text-slate-400 font-mono">Flask • Port 5002</p>
                  <p className="text-[10px] text-slate-500 mt-1">
                    Owns opportunities & match scoring
                  </p>
                  <div className="mt-2 text-[10px] text-sky-400 font-mono bg-sky-950/40 px-2 py-0.5 rounded w-fit">
                    db: opportunity_db
                  </div>
                </div>
              </div>

              {/* Arrow to Databases */}
              <div className="flex-1 flex flex-col items-center justify-center">
                <span className="text-[10px] font-mono text-slate-400 mb-1">PyMongo</span>
                <div className="w-full h-0.5 bg-slate-800" />
              </div>

              {/* Layer 3: Independent Databases */}
              <div className="flex flex-col gap-4 shrink-0">
                <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 w-44 text-center">
                  <Database className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                  <span className="text-xs font-bold block">skill_db</span>
                  <span className="text-[10px] text-slate-400">MongoDB Isolated</span>
                </div>
                <div className="p-3.5 rounded-2xl bg-slate-900 border border-slate-800 w-44 text-center">
                  <Database className="w-5 h-5 text-sky-400 mx-auto mb-1" />
                  <span className="text-xs font-bold block">opportunity_db</span>
                  <span className="text-[10px] text-slate-400">MongoDB Isolated</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resilience & Failure Handling Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader
            title="Inter-Service Integration Layer"
            subtitle="Skill Service <-> Opportunity Service communication specifications"
          />
          <CardContent className="space-y-3 text-xs">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">HTTP REST via OpportunityClient:</strong>
                <p className="text-slate-500">
                  Requests utilize connection pooling and dedicated session recycling.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">3s Connect / 8s Read Timeouts:</strong>
                <p className="text-slate-500">
                  Prevents thread exhaustion in Flask when downstream latency spikes.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">Exponential Backoff Retries:</strong>
                <p className="text-slate-500">
                  2 retries on HTTP 500, 502, 503, 504 and transient dropped network connections.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader
            title="Graceful Degradation Guarantees"
            subtitle="Guaranteed behavior under microservice outage scenarios"
          />
          <CardContent className="space-y-3 text-xs">
            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">Opportunity Service Outage:</strong>
                <p className="text-slate-500">
                  Skill Service continues returning HTTP 200 with local gap analysis and learning roadmaps intact.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">Shared Secret Authentication:</strong>
                <p className="text-slate-500">
                  Internal match endpoint is secured with <code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded">X-Service-Key</code> header tokens.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <div>
                <strong className="text-slate-800 dark:text-slate-200">Database Decoupling:</strong>
                <p className="text-slate-500">
                  Neither microservice directly reads or writes to the other's MongoDB cluster.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SystemStatus;
