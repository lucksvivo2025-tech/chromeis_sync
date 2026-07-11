frappe.ui.form.on('Customer', {
    refresh: function(frm) {
        // Stop execution cleanly if server payload isn't completely ready yet
        if (!frm.doc.__onload || frm.doc.__onload.val_paid === undefined) return;

        let d = frm.doc.__onload;
        let net_income = d.val_paid - d.val_cost;
        
        let desk_dashboard_html = `
            <div class="form-dashboard-section" style="margin-bottom: 24px; padding: 0 15px;">
                <div class="section-head" style="font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-muted); margin-bottom: 12px;">
                    📊 Account Operational Intelligence
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px;">
                    
                    <div class="report-summary-item" style="background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; padding: 12px 16px; box-shadow: var(--shadow-sm);">
                        <div class="summary-label" style="font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">👤 Client Profile</div>
                        <div style="font-size: 13px; color: var(--text-color); line-height: 1.5;">
                            <div style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;"><strong>Email:</strong> <span class="text-muted">${frm.doc.email_id || 'N/A'}</span></div>
                            <div><strong>Phone:</strong> <span class="text-muted">${frm.doc.mobile_no || 'N/A'}</span></div>
                            <div><strong>Territory:</strong> <span class="text-muted">${frm.doc.territory || 'N/A'}</span></div>
                        </div>
                    </div>

                    <div class="report-summary-item" style="background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; padding: 12px 16px; box-shadow: var(--shadow-sm);">
                        <div class="summary-label" style="font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">💰 Gross Revenue</div>
                        <div class="summary-value" style="font-size: 18px; font-weight: 700; color: var(--green-600, #22c55e);">Rs. ${d.val_paid.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                        <div class="summary-indicator text-muted" style="font-size: 11px; margin-top: 2px;">From ${d.val_paid_count} Paid Invoices</div>
                    </div>

                    <div class="report-summary-item" style="background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; padding: 12px 16px; box-shadow: var(--shadow-sm);">
                        <div class="summary-label" style="font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">⏳ Current Balance</div>
                        <div class="summary-value" style="font-size: 18px; font-weight: 700; color: ${d.val_unpaid > 0 ? 'var(--red-600, #ef4444)' : 'var(--text-muted, #64748b)'};">Rs. ${d.val_unpaid.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                        <div class="summary-indicator text-muted" style="font-size: 11px; margin-top: 2px;">${d.val_unpaid_count} Outstanding Invoices</div>
                    </div>

                    <div class="report-summary-item" style="background: var(--card-bg, #fff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; padding: 12px 16px; box-shadow: var(--shadow-sm);">
                        <div class="summary-label" style="font-size: 11px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">🛡️ Profit Position</div>
                        <div class="summary-value" style="font-size: 18px; font-weight: 700; color: var(--text-color);">Rs. ${net_income.toLocaleString(undefined, {minimumFractionDigits: 2})}</div>
                        <div class="summary-indicator text-muted" style="font-size: 11px; margin-top: 2px; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">Infra Costs: Rs. ${d.val_cost.toLocaleString()}</div>
                    </div>

                </div>

                <div style="margin-top: 12px; background: var(--bg-light-gray, #f8fafc); border: 1px solid var(--border-color, #e2e8f0); border-radius: 6px; padding: 10px 14px; font-size: 12px; display: flex; flex-wrap: wrap; gap: 20px; color: var(--text-color);">
                    <div><strong>📦 Services Traced (${d.val_services_count}):</strong> <span class="text-muted">${d.val_services_list}</span></div>
                    <div style="border-left: 1px solid var(--border-color, #e2e8f0); padding-left: 20px;"><strong>🌐 Active Allocations:</strong> <span style="font-family: monospace; color: var(--text-muted);">${d.val_assets_list}</span></div>
                </div>
            </div>
        `;
        
        // Ensure the core dashboard section container is visible
        frm.dashboard.show();
        
        // Remove old custom injection blocks if they exist to prevent duplication
        $(frm.dashboard.wrapper).find('.account-intel-section').remove();
        
        // Prepend our wide section row straight to the top of the main dashboard section wrapper
        $(frm.dashboard.wrapper).prepend(`<div class="account-intel-section">${desk_dashboard_html}</div>`);
    }
});
