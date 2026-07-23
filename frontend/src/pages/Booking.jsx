import React, { useEffect, useState } from 'react';
import PageContainer from '../components/PageContainer';
import { fetchAssets, fetchBookings, apiService } from '../services/api';
import { Calendar, Plus, X } from 'lucide-react';

function formatRange(start, end) {
  const s = new Date(start);
  const e = new Date(end);
  const sameDay = s.toDateString() === e.toDateString();
  const opts = { hour: '2-digit', minute: '2-digit' };
  return sameDay
    ? `${s.toLocaleDateString()} · ${s.toLocaleTimeString([], opts)} - ${e.toLocaleTimeString([], opts)}`
    : `${s.toLocaleString()} → ${e.toLocaleString()}`;
}

function statusStyle(status) {
  const styles = {
    UPCOMING: 'bg-blue-100 text-blue-700',
    ONGOING: 'bg-green-100 text-green-700',
    COMPLETED: 'bg-surface-100 text-surface-600',
    CANCELLED: 'bg-red-100 text-red-700',
  };
  return styles[status?.toUpperCase()] || 'bg-surface-100 text-surface-600';
}

function NewBookingModal({ onClose, onCreated }) {
  const [assets, setAssets] = useState([]);
  const [assetId, setAssetId] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [purpose, setPurpose] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [suggestedSlot, setSuggestedSlot] = useState(null);

  useEffect(() => {
    // Only bookable resources belong in this dropdown.
    fetchAssets().then((all) => setAssets(all.filter((a) => a.is_bookable)));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuggestedSlot(null);

    if (!assetId || !startTime || !endTime) {
      setError('Asset, start time, and end time are all required.');
      return;
    }

    const payload = {
      asset_id: Number(assetId),
      start_time: new Date(startTime).toISOString(),
      end_time: new Date(endTime).toISOString(),
    };
    if (purpose.trim()) payload.purpose = purpose.trim();

    setSubmitting(true);
    try {
      const created = await apiService.post('bookings', payload);
      onCreated(created);
      onClose();
    } catch (err) {
      // Backend returns 409 with BookingConflictDetail, sometimes including
      // a suggested_slot — surface that if present instead of just the message.
      setError(err.message || 'Booking failed — that slot may already be taken.');
      if (err.detail?.suggested_slot) setSuggestedSlot(err.detail.suggested_slot);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-surface-800 rounded-lg shadow-lg w-full max-w-md">
        <div className="flex justify-between items-center px-6 py-4 border-b border-surface-200 dark:border-surface-700">
          <h2 className="text-lg font-semibold">New Booking</h2>
          <button onClick={onClose}><X className="w-5 h-5" /></button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded">
              {error}
              {suggestedSlot && (
                <div className="mt-1 text-xs">
                  Next available: {formatRange(suggestedSlot.start_time, suggestedSlot.end_time)}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-1">Resource *</label>
            <select value={assetId} onChange={(e) => setAssetId(e.target.value)} className="w-full p-2 border rounded bg-surface-50">
              <option value="">
                {assets.length === 0 ? 'No bookable resources found' : 'Select a resource'}
              </option>
              {assets.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start *</label>
              <input type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} className="w-full p-2 border rounded bg-surface-50" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End *</label>
              <input type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} className="w-full p-2 border rounded bg-surface-50" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Purpose</label>
            <input value={purpose} onChange={(e) => setPurpose(e.target.value)} className="w-full p-2 border rounded bg-surface-50" placeholder="e.g. Sprint planning" />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded text-sm border">Cancel</button>
            <button type="submit" disabled={submitting} className="px-4 py-2 rounded text-sm bg-brand-teal text-white font-medium disabled:opacity-60">
              {submitting ? 'Booking...' : 'Confirm Booking'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Booking() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const load = () => fetchBookings().then((data) => { setBookings(data); setLoading(false); });

  useEffect(() => { load(); }, []);

  return (
    <PageContainer title="Resource Booking" description="Manage shared asset schedules.">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white dark:bg-surface-800 p-6 border rounded-lg shadow-sm">
            <h2 className="font-medium mb-4">Active Bookings</h2>
            {loading && <p className="text-sm text-surface-500">Loading...</p>}
            {!loading && bookings.length === 0 && (
              <p className="text-sm text-surface-500">No bookings yet.</p>
            )}
            <div className="space-y-3">
              {bookings.map((b) => (
                <div key={b.id} className="p-4 border rounded-md flex justify-between items-center bg-surface-50 dark:bg-surface-900">
                  <div className="flex items-center gap-3">
                    <Calendar className="w-5 h-5 text-brand-teal" />
                    <div>
                      <div>{b.purpose || `Booking #${b.id}`}</div>
                      <span className={`text-xs px-2 py-0.5 rounded ${statusStyle(b.effective_status)}`}>
                        {b.effective_status}
                      </span>
                    </div>
                  </div>
                  <span className="text-sm font-mono">{formatRange(b.start_time, b.end_time)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="h-full min-h-[150px] border-2 border-dashed border-surface-300 rounded-lg flex flex-col items-center justify-center gap-2 hover:border-brand-teal hover:text-brand-teal transition"
        >
          <Plus className="w-8 h-8" />
          <span className="font-medium">New Booking</span>
        </button>
      </div>

      {showModal && (
        <NewBookingModal onClose={() => setShowModal(false)} onCreated={() => load()} />
      )}
    </PageContainer>
  );
}