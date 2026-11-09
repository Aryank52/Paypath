import React, { useEffect, useState } from 'react';
import { FileCheck2, ShieldCheck, RefreshCw, Clock, User, Cpu, Server } from 'lucide-react';
import { api } from '../services/api';

export const AuditLogView: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLogs = () => {
    setIsLoading(true);
    api.getAuditLogs()
      .then(setLogs)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
            <span>Immutable Audit Trail & Observability</span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              Tamper-Resistant Log
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Application-level chronological record of every financial mutation, policy evaluation, and agent execution.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          title="Refresh Logs"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-4">
        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-500">Loading audit trail...</div>
        ) : logs.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">No audit events recorded yet.</div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {logs.map((log) => (
              <div key={log.id} className="py-3 px-2 flex items-center justify-between hover:bg-slate-800/30 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center">
                    {log.actor_type === 'USER' ? (
                      <User className="w-4 h-4 text-indigo-400" />
                    ) : log.actor_type === 'AGENT' ? (
                      <Cpu className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Server className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-200">{log.action}</div>
                    <div className="text-[11px] text-slate-400">
                      Target: <span className="font-mono text-slate-300">{log.resource_type}:{log.resource_id}</span>
                    </div>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-[11px] text-slate-400">{new Date(log.created_at).toLocaleString()}</div>
                  <div className="text-[10px] text-slate-400">Actor: {log.actor_type} ({log.actor_id || 'System'})</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
