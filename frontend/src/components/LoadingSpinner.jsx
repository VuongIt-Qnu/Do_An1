/**
 * LoadingSpinner Component
 * Centered spinner for loading states.
 * fullPage=true renders centered in the viewport.
 */
import React from 'react';

export default function LoadingSpinner({ fullPage = false, message = 'Đang tải...' }) {
  const content = (
    <div className="text-center py-5">
      <div className="spinner-border text-primary" role="status" style={{ width: '3rem', height: '3rem' }}>
        <span className="visually-hidden">{message}</span>
      </div>
      <p className="mt-3 text-muted">{message}</p>
    </div>
  );

  if (fullPage) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ minHeight: '80vh' }}
      >
        {content}
      </div>
    );
  }

  return content;
}
