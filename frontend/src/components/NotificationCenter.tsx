import React, { useEffect, useState } from 'react';
import { Bell, Check, Clock, ShieldCheck, AlertTriangle, RotateCcw, X, ExternalLink } from 'lucide-react';
import { useStore } from '../store/useStore';
import { api } from '../services/api';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  action_url?: string;
  created_at: string;
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const NotificationCenter: React.FC<Props> = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { setActiveTab, setNotificationCount } = useStore();

  const fetchNotifications = () => {
    setIsLoading(true);
    api.getNotifications()
      .then((data) => {
        setNotifications(data);
        const unread = data.filter((n: NotificationItem) => !n.is_read).length;
        setNotificationCount(unread);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen]);

  const handleMarkAsRead = async (id: string) => {
    try {
      await api.markNotificationAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      setNotificationCount(
        notifications.filter((n) => n.id !== id && !n.is_read).length
      );
    } catch (err) {
      console.error(err);
    }
  };

  const handleActionClick = (notif: NotificationItem) => {
    handleMarkAsRead(notif.id);
    onClose();
    if (notif.notification_type === 'REFUND_RECOMMENDED' || notif.notification_type === 'PAYMENT_APPROVAL_REQUIRED') {
      setActiveTab('reclaim');
    } else if (notif.notification_type === 'ANOMALY_DETECTED') {
      setActiveTab('recovery');
    } else {
      setActiveTab('transactions');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
      <div className="w-full max-w-sm bg-slate-900 border-l border-slate-800 h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4 text-indigo-400" />
            <h2 className="text-xs font-bold text-white uppercase tracking-wider">Notification Center</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* List Body */}
        <div className="p-4 flex-1 overflow-y-auto space-y-3">
          {isLoading ? (
            <div className="py-8 text-center text-xs text-slate-500">Loading notifications...</div>
          ) : notifications.length === 0 ? (
            <div className="py-8 text-center text-xs text-slate-500">No active notifications.</div>
          ) : (
            notifications.map((notif) => (
              <div
                key={notif.id}
                className={`p-3 rounded-xl border transition-all ${
                  notif.is_read
                    ? 'bg-slate-950/40 border-slate-800/80 text-slate-400'
                    : 'bg-slate-900 border-indigo-500/30 shadow-md shadow-indigo-500/5 text-slate-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-1.5 font-bold text-xs text-white">
                    {notif.notification_type === 'REFUND_RECOMMENDED' ? (
                      <RotateCcw className="w-3.5 h-3.5 text-emerald-400" />
                    ) : notif.notification_type === 'ANOMALY_DETECTED' ? (
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    ) : (
                      <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
                    )}
                    <span>{notif.title}</span>
                  </div>
                  {!notif.is_read && (
                    <button
                      onClick={() => handleMarkAsRead(notif.id)}
                      className="text-[10px] text-indigo-400 hover:text-indigo-300 font-medium"
                      title="Mark as Read"
                    >
                      <Check className="w-3 h-3" />
                    </button>
                  )}
                </div>

                <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                  {notif.message}
                </p>

                <div className="mt-2.5 flex items-center justify-between text-[10px] text-slate-500">
                  <span>{new Date(notif.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <button
                    onClick={() => handleActionClick(notif)}
                    className="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center space-x-1"
                  >
                    <span>View Action</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-800 bg-slate-950 text-center text-[10px] text-slate-500">
          In-App & Transactional Email Provider Synchronized
        </div>
      </div>
    </div>
  );
};

