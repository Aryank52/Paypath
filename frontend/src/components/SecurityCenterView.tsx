import React, { useState } from 'react';
import { 
  ShieldCheck, 
  KeyRound, 
  Lock, 
  Smartphone, 
  CheckCircle2, 
  AlertCircle, 
  QrCode, 
  Copy,
  LogOut,
  Laptop
} from 'lucide-react';
import { useStore } from '../store/useStore';
import { api } from '../services/api';

export const SecurityCenterView: React.FC = () => {
  const { currentUser, updateCurrentUser } = useStore();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  // MFA Setup State
  const [mfaSecret, setMfaSecret] = useState<string | null>(null);
  const [mfaUri, setMfaUri] = useState<string | null>(null);
  const [mfaCode, setMfaCode] = useState('');
  const [mfaLoading, setMfaLoading] = useState(false);
  const [mfaSuccess, setMfaSuccess] = useState<string | null>(null);
  const [mfaError, setMfaError] = useState<string | null>(null);

  const handleInitiateMfa = async () => {
    setMfaLoading(true);
    setMfaError(null);
    try {
      const res = await api.setupMFA();
      setMfaSecret(res.secret);
      setMfaUri(res.otpauth_url);
    } catch (err: any) {
      setMfaError(err.message || 'Failed to initialize MFA setup.');
    } finally {
      setMfaLoading(false);
    }
  };

  const handleEnableMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    setMfaLoading(true);
    setMfaError(null);
    try {
      await api.enableMFA(mfaCode.trim());
      updateCurrentUser({ mfa_enabled: true });
      setMfaSuccess('Two-factor authentication has been enabled on your account.');
      setMfaSecret(null);
      setMfaCode('');
    } catch (err: any) {
      setMfaError(err.message || 'Invalid verification code.');
    } finally {
      setMfaLoading(false);
    }
  };

  const handleDisableMfa = async (e: React.FormEvent) => {
    e.preventDefault();
    setMfaLoading(true);
    setMfaError(null);
    try {
      await api.disableMFA(mfaCode.trim());
      updateCurrentUser({ mfa_enabled: false });
      setMfaSuccess('Two-factor authentication has been disabled.');
      setMfaCode('');
    } catch (err: any) {
      setMfaError(err.message || 'Invalid verification code.');
    } finally {
      setMfaLoading(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);

    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }

    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters long.');
      return;
    }

    setPasswordLoading(true);
    try {
      const res = await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword
      });
      setPasswordSuccess(res.message);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password. Current password may be incorrect.');
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in duration-200">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Security & Access Center</h1>
        <p className="text-slate-400 text-sm mt-1">
          Two-factor authentication, active sessions, and password management.
        </p>
      </div>

      {/* MFA SECTION */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Smartphone className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Two-Factor Authentication (TOTP)</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Protect mutations and logins with Google Authenticator, Authy, or 1Password.
              </p>
            </div>
          </div>
          <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${currentUser?.mfa_enabled ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-800 text-slate-400'}`}>
            {currentUser?.mfa_enabled ? 'Active / Protected' : 'Disabled'}
          </span>
        </div>

        {mfaSuccess && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{mfaSuccess}</span>
          </div>
        )}
        {mfaError && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{mfaError}</span>
          </div>
        )}

        {!currentUser?.mfa_enabled && !mfaSecret && (
          <button
            type="button"
            onClick={handleInitiateMfa}
            disabled={mfaLoading}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/20 cursor-pointer disabled:opacity-50"
          >
            <KeyRound className="w-4 h-4" />
            <span>{mfaLoading ? 'Configuring...' : 'Set Up Two-Factor Authentication'}</span>
          </button>
        )}

        {/* Setup In Progress */}
        {!currentUser?.mfa_enabled && mfaSecret && (
          <div className="mt-4 p-5 rounded-2xl bg-slate-950 border border-slate-800 space-y-4">
            <div className="text-xs text-slate-300">
              <span className="font-semibold block mb-1">Step 1: Enter Secret Key in Authenticator App</span>
              <div className="flex items-center gap-2 mt-2">
                <code className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-indigo-300 select-all">
                  {mfaSecret}
                </code>
              </div>
            </div>

            <form onSubmit={handleEnableMfa} className="space-y-3 pt-2">
              <label className="block text-xs font-medium text-slate-300">Step 2: Enter 6-Digit Code to Confirm</label>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="w-40 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-800 text-sm font-mono tracking-widest text-white text-center focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  disabled={mfaLoading || mfaCode.length !== 6}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs cursor-pointer disabled:opacity-50"
                >
                  {mfaLoading ? 'Activating...' : 'Activate MFA'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Disable MFA Form */}
        {currentUser?.mfa_enabled && (
          <form onSubmit={handleDisableMfa} className="pt-2 flex items-center gap-3">
            <input
              type="text"
              maxLength={6}
              required
              value={mfaCode}
              onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
              placeholder="Current 6-digit code"
              className="w-48 px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-white text-center focus:outline-none focus:border-rose-500"
            />
            <button
              type="submit"
              disabled={mfaLoading || mfaCode.length !== 6}
              className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-xs cursor-pointer disabled:opacity-50"
            >
              {mfaLoading ? 'Disabling...' : 'Disable Two-Factor Auth'}
            </button>
          </form>
        )}
      </div>

      {/* PASSWORD SECTION */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">Change Account Password</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Requires your existing password to verify identity.
            </p>
          </div>
        </div>

        {passwordSuccess && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{passwordSuccess}</span>
          </div>
        )}
        {passwordError && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{passwordError}</span>
          </div>
        )}

        <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Current Password</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••••••"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">New Password</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min 8 characters"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Confirm New Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-enter new password"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={passwordLoading}
            className="px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs flex items-center gap-2 shadow-lg shadow-sky-600/20 cursor-pointer disabled:opacity-50"
          >
            <Lock className="w-4 h-4" />
            <span>{passwordLoading ? 'Updating Password...' : 'Update Password'}</span>
          </button>
        </form>
      </div>

      {/* ACTIVE SESSIONS */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center">
              <Laptop className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Active Device Sessions</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Current and recent authorized logins.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
              <div>
                <span className="text-xs font-semibold text-white block">Current Active Session (Web Client)</span>
                <span className="text-[11px] text-slate-500">127.0.0.1 • TLS 1.3 • JWT Bearer Token</span>
              </div>
            </div>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              Active Now
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
