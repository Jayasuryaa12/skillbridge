import React, { useState, useEffect } from 'react';
import { CloudLightning, CheckCircle2, X, RefreshCw } from 'lucide-react';
import { registerColdStartHandler } from '../../api/client';

export const ColdStartBanner = () => {
  const [wakeState, setWakeState] = useState({
    isWakingUp: false,
    justAwakened: false,
    message: '',
    service: '',
  });
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    registerColdStartHandler((state) => {
      setWakeState(state);
      if (state.isWakingUp) {
        setSeconds(0);
      }
    });
  }, []);

  useEffect(() => {
    let interval = null;
    if (wakeState.isWakingUp) {
      interval = setInterval(() => {
        setSeconds((s) => s + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [wakeState.isWakingUp]);

  useEffect(() => {
    let timer = null;
    if (wakeState.justAwakened) {
      timer = setTimeout(() => {
        setWakeState((prev) => ({ ...prev, justAwakened: false }));
      }, 4000);
    }
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [wakeState.justAwakened]);

  if (!wakeState.isWakingUp && !wakeState.justAwakened) {
    return null;
  }

  return (
    <div
      className={`w-full px-4 py-2.5 transition-all duration-300 text-xs flex items-center justify-between border-b ${
        wakeState.isWakingUp
          ? 'bg-amber-500/10 dark:bg-amber-950/40 border-amber-500/30 text-amber-900 dark:text-amber-200'
          : 'bg-emerald-500/10 dark:bg-emerald-950/40 border-emerald-500/30 text-emerald-900 dark:text-emerald-200'
      }`}
    >
      <div className="flex items-center gap-2.5 max-w-5xl mx-auto flex-1">
        {wakeState.isWakingUp ? (
          <div className="flex items-center gap-2 font-medium">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-600 dark:text-amber-400 shrink-0" />
            <span>
              <strong>Waking Up Microservices:</strong> Render free-tier instances sleep after inactivity.
              Container is currently spinning up ({seconds}s elapsed)...
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-2 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
            <span>
              <strong>Services Connected:</strong> Microservices are now awake and responding.
            </span>
          </div>
        )}
      </div>

      <button
        onClick={() => setWakeState({ isWakingUp: false, justAwakened: false, message: '' })}
        className="p-1 hover:bg-slate-200/50 dark:hover:bg-slate-800/50 rounded transition-colors text-slate-500"
        title="Dismiss"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default ColdStartBanner;
