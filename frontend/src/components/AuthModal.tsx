import React, { useState } from 'react';
import { 
  X, 
  ShieldCheck, 
  Lock, 
  Mail, 
  User, 
  Phone, 
  CheckCircle2, 
  AlertCircle, 
  ArrowRight,
  KeyRound,
  Eye,
  EyeOff
} from 'lucide-react';
import { useStore, AuthModalType } from '../store/useStore';
import { api } from '../services/api';

export const AuthModal: React.FC = () => {
  const { 
    authModal, 
    setAuthModal, 
    loginUser, 
    mfaPending, 
    setMfaPending,
    resetToken,
    setResetToken,
    verificationToken,
    setVerificationToken
  } = useStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [mobileNumber, setMobileNumber] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [tokenInput, setTokenInput] = useState('');
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!authModal) return null;

  // Password Strength Checklist
  const hasMinLength = password.length >= 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecial = /[^A-Za-z0-9]/.test(password);
  const isPasswordStrong = hasMinLength && hasUppercase && hasLowercase && hasNumber && hasSpecial;

  const handleClose = () => {
    setAuthModal(null);
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await api.login({ email, password, mfa_code: mfaCode || undefined });
      if (res.mfa_required) {
        setMfaPending({ user_id: res.user_id, email: res.email });
        setAuthModal('mfa');
        setSuccessMsg('Two-factor authentication required. Enter your 6-digit code.');
        return;
      }

      loginUser(res.access_token, {
        id: res.user_id,
        email: res.email,
        full_name: res.full_name,
        role: res.role as any,
        is_active: true,
        email_verified: true,
        mfa_enabled: false,
        preferred_currency: 'USD'
      });
      handleClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!isPasswordStrong) {
      setErrorMsg('Please satisfy all password complexity requirements.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    if (!termsAccepted) {
      setErrorMsg('You must agree to the Terms of Service and Privacy Policy.');
      return;
    }

    setLoading(true);
    try {
      await api.register({
        email,
        password,
        full_name: fullName,
        mobile_number: mobileNumber || undefined
      });
      setSuccessMsg('Account registered successfully! Please log in or check your verification email.');
      setAuthModal('login');
    } catch (err: any) {
      setErrorMsg(err.message || 'Registration failed. Email may already be in use.');
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mfaPending) return;
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await api.login({ 
        email: mfaPending.email, 
        password, 
        mfa_code: mfaCode.trim() 
      });

      loginUser(res.access_token, {
        id: res.user_id,
        email: res.email,
        full_name: res.full_name,
        role: res.role as any,
        is_active: true,
        email_verified: true,
        mfa_enabled: true,
        preferred_currency: 'USD'
      });
      handleClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Invalid two-factor authentication code.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      const res = await api.requestPasswordReset(email);
      setSuccessMsg(res.message);
      if (res.dev_reset_token) {
        setTokenInput(res.dev_reset_token);
        setResetToken(res.dev_reset_token);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to dispatch reset instructions.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!isPasswordStrong) {
      setErrorMsg('Please satisfy all password complexity requirements.');
      return;
    }

    setLoading(true);
    try {
      const token = resetToken || tokenInput;
      const res = await api.confirmPasswordReset(token, password);
      setSuccessMsg(res.message);
      setAuthModal('login');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to reset password. Token may be expired.');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setLoading(true);

    try {
      const token = verificationToken || tokenInput;
      const res = await api.verifyEmail(token);
      setSuccessMsg(res.message);
      setAuthModal('login');
    } catch (err: any) {
      setErrorMsg(err.message || 'Email verification failed. Token may be invalid or expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl text-slate-100">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Icon & Title */}
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-3">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-white">
            {authModal === 'login' && 'Sign in to PayPath'}
            {authModal === 'signup' && 'Create your PayPath account'}
            {authModal === 'mfa' && 'Two-Factor Authentication'}
            {authModal === 'forgot-password' && 'Reset your password'}
            {authModal === 'reset-password' && 'Enter your new password'}
            {authModal === 'verify-email' && 'Verify your email address'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {authModal === 'login' && 'Secure access to transaction intelligence and payment control'}
            {authModal === 'signup' && 'Join the verified policy-aware payment ecosystem'}
            {authModal === 'mfa' && 'Enter the 6-digit code from your authenticator app'}
            {authModal === 'forgot-password' && 'Enter your account email to receive a secure link'}
            {authModal === 'reset-password' && 'Choose a secure password for your account'}
            {authModal === 'verify-email' && 'Enter your single-use verification token'}
          </p>
        </div>

        {/* Feedback Alerts */}
        {errorMsg && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* LOGIN FORM */}
        {authModal === 'login' && (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.chen@example.com"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-medium text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => setAuthModal('forgot-password')}
                  className="text-xs text-indigo-400 hover:text-indigo-300 cursor-pointer"
                >
                  Forgot password?
                </button>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={() => setAuthModal('signup')}
                className="text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer"
              >
                Sign up free
              </button>
            </div>
          </form>
        )}

        {/* SIGNUP FORM */}
        {authModal === 'signup' && (
          <form onSubmit={handleSignup} className="space-y-3.5">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Alex Chen"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.chen@example.com"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Mobile Number (Optional)</label>
              <div className="relative">
                <Phone className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="tel"
                  value={mobileNumber}
                  onChange={(e) => setMobileNumber(e.target.value)}
                  placeholder="+1 (555) 234-5678"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Min 8 chars with upper, lower, digit, symbol"
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              {/* Real-Time Password Checklist */}
              <div className="grid grid-cols-2 gap-1.5 mt-2 text-[11px]">
                <div className={`flex items-center gap-1 ${hasMinLength ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  <span>8+ characters</span>
                </div>
                <div className={`flex items-center gap-1 ${hasUppercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Uppercase letter</span>
                </div>
                <div className={`flex items-center gap-1 ${hasLowercase ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Lowercase letter</span>
                </div>
                <div className={`flex items-center gap-1 ${hasNumber && hasSpecial ? 'text-emerald-400' : 'text-slate-500'}`}>
                  <CheckCircle2 className="w-3 h-3" />
                  <span>Number & symbol</span>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Confirm Password</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex items-start gap-2 pt-1 text-xs text-slate-400">
              <input
                type="checkbox"
                id="terms"
                required
                checked={termsAccepted}
                onChange={(e) => setTermsAccepted(e.target.checked)}
                className="mt-0.5 rounded border-slate-800 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
              />
              <label htmlFor="terms">
                I agree to the Terms of Service and acknowledge the Privacy Policy.
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !isPasswordStrong}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Already have an account?{' '}
              <button
                type="button"
                onClick={() => setAuthModal('login')}
                className="text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer"
              >
                Sign in
              </button>
            </div>
          </form>
        )}

        {/* MFA CODE CHALLENGE */}
        {authModal === 'mfa' && (
          <form onSubmit={handleMfaSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">6-Digit Authenticator Code</label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  maxLength={6}
                  required
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white text-center tracking-widest font-mono text-lg focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || mfaCode.length !== 6}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Verifying...' : 'Verify & Continue'}
            </button>
          </form>
        )}

        {/* FORGOT PASSWORD FORM */}
        {authModal === 'forgot-password' && (
          <form onSubmit={handleForgotPassword} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Registered Account Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex.chen@example.com"
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {tokenInput && (
              <div className="p-3 bg-slate-950 border border-indigo-500/30 rounded-xl text-xs text-indigo-300">
                <span className="font-semibold block mb-1">Development Reset Token:</span>
                <span className="font-mono text-[11px] break-all">{tokenInput}</span>
                <button
                  type="button"
                  onClick={() => setAuthModal('reset-password')}
                  className="mt-2 text-indigo-400 hover:text-white underline block"
                >
                  Proceed to Reset Password
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Sending Request...' : 'Send Reset Link'}
            </button>

            <div className="text-center pt-2 text-xs text-slate-400">
              Remembered your password?{' '}
              <button
                type="button"
                onClick={() => setAuthModal('login')}
                className="text-indigo-400 hover:text-indigo-300 font-medium cursor-pointer"
              >
                Sign in
              </button>
            </div>
          </form>
        )}

        {/* RESET PASSWORD FORM */}
        {authModal === 'reset-password' && (
          <form onSubmit={handleResetPassword} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Reset Token</label>
              <input
                type="text"
                required
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                placeholder="Paste your reset token"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">New Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Choose a strong password"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !isPasswordStrong}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Updating Password...' : 'Update Password'}
            </button>
          </form>
        )}

        {/* VERIFY EMAIL FORM */}
        {authModal === 'verify-email' && (
          <form onSubmit={handleVerifyEmail} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Verification Token</label>
              <input
                type="text"
                required
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                placeholder="Paste your email verification token"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all shadow-lg shadow-indigo-600/20 disabled:opacity-50 cursor-pointer"
            >
              {loading ? 'Verifying...' : 'Verify Email'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
