/**
 * PaymentInstructions
 * Displays payment details for a booking based on the chosen payment method.
 * Used in BookingPage success screen and BookingDetailPage.
 */
import React, { useState } from 'react';
import { toast } from 'react-toastify';

const VND = (v) =>
  new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND', maximumFractionDigits: 0 }).format(v ?? 0);

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      toast.success('Đã sao chép!');
      setTimeout(() => setCopied(false), 2000);
    });
  };
  return (
    <button type="button" className="btn btn-sm btn-outline-secondary ms-2 py-0" onClick={handleCopy}>
      <i className={`bi ${copied ? 'bi-check2' : 'bi-clipboard'} me-1`}></i>
      {copied ? 'Đã copy' : 'Copy'}
    </button>
  );
}

function InfoRow({ label, value, copyable = false }) {
  if (!value) return null;
  return (
    <div className="d-flex justify-content-between align-items-center py-2 border-bottom">
      <span className="text-muted small">{label}</span>
      <div className="d-flex align-items-center">
        <span className="fw-semibold small text-end" style={{ maxWidth: 260 }}>{value}</span>
        {copyable && <CopyButton text={value} />}
      </div>
    </div>
  );
}

// ── Bank Transfer ─────────────────────────────────────────────────────────────
function BankTransferInfo({ info, paymentNote, amount }) {
  const bt = info?.bank_transfer || {};
  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <div className="bg-primary bg-opacity-10 rounded p-2">
          <i className="bi bi-bank text-primary fs-4"></i>
        </div>
        <div>
          <div className="fw-bold">Chuyển khoản ngân hàng</div>
          <div className="text-muted small">Chuyển khoản và gửi bill xác nhận</div>
        </div>
      </div>

      <div className="card border-primary border-opacity-25 mb-3">
        <div className="card-body py-2 px-3">
          <InfoRow label="Ngân hàng"      value={bt.bank_name} />
          <InfoRow label="Số tài khoản"   value={bt.account_number} copyable />
          <InfoRow label="Chủ tài khoản"  value={bt.account_holder} />
          <InfoRow label="Chi nhánh"       value={bt.bank_branch} />
          <InfoRow label="Số tiền"         value={VND(amount)} />
          <div className="mt-2 pt-2">
            <div className="text-muted small mb-1">Nội dung chuyển khoản</div>
            <div className="d-flex align-items-center gap-2 p-2 bg-warning bg-opacity-10 rounded border border-warning border-opacity-25">
              <code className="flex-grow-1 small fw-bold">{paymentNote}</code>
              <CopyButton text={paymentNote} />
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-info border-0 small py-2">
        <i className="bi bi-info-circle me-1"></i>
        Sau khi chuyển khoản, vui lòng chụp màn hình giao dịch và gửi cho chúng tôi để xác nhận.
      </div>
    </div>
  );
}

// ── MoMo ─────────────────────────────────────────────────────────────────────
function MomoInfo({ info, paymentNote, amount }) {
  const momo = info?.momo || {};
  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <div className="rounded p-2" style={{ background: '#d82d8b20' }}>
          <i className="bi bi-phone fs-4" style={{ color: '#d82d8b' }}></i>
        </div>
        <div>
          <div className="fw-bold">Ví MoMo</div>
          <div className="text-muted small">Quét QR hoặc chuyển qua số điện thoại</div>
        </div>
      </div>

      <div className="row g-3 mb-3">
        {momo.momo_qr && (
          <div className="col-auto mx-auto">
            <div className="border rounded p-2 text-center">
              <img src={momo.momo_qr} alt="MoMo QR" style={{ width: 180, height: 180, objectFit: 'contain' }}
                onError={e => { e.target.style.display = 'none'; }} />
              <div className="text-muted small mt-1">Quét QR để thanh toán</div>
            </div>
          </div>
        )}
        <div className="col">
          <div className="card border-0 bg-light h-100">
            <div className="card-body py-2 px-3">
              <InfoRow label="Số ví MoMo" value={momo.momo_number} copyable />
              <InfoRow label="Số tiền"    value={VND(amount)} />
              <div className="mt-2 pt-2">
                <div className="text-muted small mb-1">Nội dung chuyển</div>
                <div className="d-flex align-items-center gap-2 p-2 bg-white rounded border">
                  <code className="flex-grow-1 small fw-bold">{paymentNote}</code>
                  <CopyButton text={paymentNote} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-info border-0 small py-2">
        <i className="bi bi-info-circle me-1"></i>
        Nhập đúng nội dung chuyển tiền để chúng tôi xác nhận đơn hàng của bạn.
      </div>
    </div>
  );
}

// ── Cash ──────────────────────────────────────────────────────────────────────
function CashInfo({ amount }) {
  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <div className="bg-success bg-opacity-10 rounded p-2">
          <i className="bi bi-cash-stack text-success fs-4"></i>
        </div>
        <div>
          <div className="fw-bold">Tiền mặt tại quầy</div>
          <div className="text-muted small">Thanh toán khi đến nhận phòng</div>
        </div>
      </div>

      <div className="card border-success border-opacity-25 mb-3">
        <div className="card-body">
          <div className="text-center py-3">
            <i className="bi bi-building fs-1 text-success mb-2 d-block"></i>
            <h5 className="fw-bold mb-1">Thanh toán tại quầy lễ tân</h5>
            <p className="text-muted small mb-2">
              Vui lòng mang theo mã đặt phòng khi đến check-in
            </p>
            <div className="d-inline-block bg-success bg-opacity-10 rounded px-3 py-2">
              <span className="fw-bold text-success fs-5">{VND(amount)}</span>
            </div>
          </div>
          <hr />
          <ul className="list-unstyled small text-muted mb-0">
            <li className="mb-1"><i className="bi bi-check-circle text-success me-2"></i>Thanh toán khi đến nhận phòng (14:00)</li>
            <li className="mb-1"><i className="bi bi-check-circle text-success me-2"></i>Chấp nhận tiền mặt VND</li>
            <li><i className="bi bi-info-circle text-info me-2"></i>Vui lòng đến đúng giờ để tránh mất đặt phòng</li>
          </ul>
        </div>
      </div>

      <div className="alert alert-warning border-0 small py-2">
        <i className="bi bi-exclamation-triangle me-1"></i>
        Booking của bạn đang ở trạng thái <strong>Chờ thanh toán</strong>.
        Sẽ được xác nhận sau khi thanh toán tại quầy.
      </div>
    </div>
  );
}

// ── QR Code ───────────────────────────────────────────────────────────────────
function QRCodeInfo({ info, paymentNote, amount }) {
  const qr = info?.qr || {};
  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <div className="bg-dark bg-opacity-10 rounded p-2">
          <i className="bi bi-qr-code fs-4 text-dark"></i>
        </div>
        <div>
          <div className="fw-bold">Thanh toán QR</div>
          <div className="text-muted small">Quét mã QR bằng app ngân hàng</div>
        </div>
      </div>

      <div className="text-center mb-3">
        {qr.qr_code_url ? (
          <div className="d-inline-block border rounded p-3">
            <img src={qr.qr_code_url} alt="QR Code" style={{ width: 200, height: 200, objectFit: 'contain' }}
              onError={e => { e.target.style.display = 'none'; }} />
            <div className="text-muted small mt-2">Quét bằng app ngân hàng bất kỳ</div>
          </div>
        ) : (
          <div className="bg-light rounded p-4 text-muted">
            <i className="bi bi-qr-code fs-1 d-block mb-2"></i>
            QR code chưa được cấu hình
          </div>
        )}
      </div>

      <div className="card border-0 bg-light mb-3">
        <div className="card-body py-2 px-3">
          <InfoRow label="Số tiền" value={VND(amount)} />
          <div className="mt-2 pt-2">
            <div className="text-muted small mb-1">Nội dung</div>
            <div className="d-flex align-items-center gap-2 p-2 bg-white rounded border">
              <code className="flex-grow-1 small fw-bold">{paymentNote}</code>
              <CopyButton text={paymentNote} />
            </div>
          </div>
        </div>
      </div>

      <div className="alert alert-info border-0 small py-2">
        <i className="bi bi-info-circle me-1"></i>
        Mở app ngân hàng → Quét QR → Xác nhận thanh toán. Booking sẽ được xác nhận trong vài phút.
      </div>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
/**
 * Props (two supported formats):
 *
 * Format A — new structured format from GET /api/payments/info/:id or create_booking:
 *   paymentInstructions: { method, amount, payment_note, status, instructions: {...} }
 *
 * Format B — legacy: payment (Payment model dict) + ownerPaymentInfo (hotel.payment_info_dict())
 */
export default function PaymentInstructions({ payment, ownerPaymentInfo, paymentInstructions }) {
  // ── Normalise input to a single shape ──────────────────────────────────────
  let method, note, amount, instr;

  if (paymentInstructions) {
    // Format A (preferred)
    method = paymentInstructions.method;
    note   = paymentInstructions.payment_note || '';
    amount = paymentInstructions.amount || 0;
    instr  = paymentInstructions.instructions || {};
  } else if (payment) {
    // Format B (legacy) — convert ownerPaymentInfo into instr shape
    method = payment.method;
    note   = payment.payment_note || '';
    amount = payment.amount || 0;
    const raw = ownerPaymentInfo || {};
    instr = {
      // bank_transfer
      bank_name:      raw.bank_transfer?.bank_name,
      account_number: raw.bank_transfer?.account_number,
      account_holder: raw.bank_transfer?.account_holder,
      bank_branch:    raw.bank_transfer?.bank_branch,
      // momo
      momo_number: raw.momo?.momo_number,
      momo_qr:     raw.momo?.momo_qr,
      // qr
      qr_code_url:    raw.qr?.qr_code_url,
      payment_note:   note,
    };
  } else {
    return null;
  }

  const hasNoInfo = method !== 'CASH' &&
    !instr.account_number && !instr.momo_number && !instr.qr_code_url;

  if (hasNoInfo) {
    return (
      <div className="alert alert-secondary small">
        <i className="bi bi-info-circle me-1"></i>
        Thông tin thanh toán chưa được cấu hình. Vui lòng liên hệ khách sạn.
      </div>
    );
  }

  // ── Render by method ───────────────────────────────────────────────────────
  // Pass flattened `instr` so each sub-component reads fields directly
  switch (method) {
    case 'BANK_TRANSFER':
      return <BankTransferInfo info={{ bank_transfer: instr }} paymentNote={note} amount={amount} />;
    case 'MOMO':
      return <MomoInfo info={{ momo: instr }} paymentNote={note} amount={amount} />;
    case 'CASH':
      return <CashInfo amount={amount} />;
    case 'QR_CODE':
      return <QRCodeInfo info={{ qr: instr }} paymentNote={note} amount={amount} />;
    default:
      return null;
  }
}
