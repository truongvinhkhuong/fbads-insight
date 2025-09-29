// Pivot Advanced: table + line + pies based on dailyTrackingData

function safeInt(v){ try{ return parseInt(v||0); } catch(_){ return 0; } }
function safeFloat(v){ try{ return parseFloat(v||0); } catch(_){ return 0; } }

function updatePivotAdvanced(data){
    if(!data || !data.daily){ return; }
    renderPivotAdvancedTable(data.daily);
    renderPivotAdvancedLine(data.daily);
    fetchPivotAdvancedBreakdowns();
}

function renderPivotAdvancedTable(rows){
    const tbody=document.getElementById('pivot-adv-table');
    if(!tbody) return;
    tbody.innerHTML='';
    let totalSpend=0, totalReach=0, totalImpr=0, totalNew=0, totalEng=0, totalPV=0;
    rows.forEach(day=>{
        const spend=safeFloat(day.spend);
        const reach=safeInt(day.reach);
        const impr=safeInt(day.impressions);
        const newMsg=safeInt(day.messaging_new_contacts || 0);
        const eng=safeInt(day.post_engagement || 0);
        const pv=safeFloat(day.purchase_value || 0);
        const cpm = impr>0 ? (spend/impr)*1000 : 0;
        const cpc = safeInt(day.clicks)>0 ? (spend/safeInt(day.clicks)) : 0;
        const cpNew = newMsg>0 ? (spend/newMsg) : 0;

        totalSpend+=spend; totalReach+=reach; totalImpr+=impr; totalNew+=newMsg; totalEng+=eng; totalPV+=pv;

        const tr=document.createElement('tr');
        tr.innerHTML=
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${new Date(day.date_start||day.date).toLocaleDateString('vi-VN')}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(spend)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(reach)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(impr)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(newMsg)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(cpNew)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${VND_FMT.format(pv)}</td>`+
            `<td class="px-2 py-2 whitespace-nowrap text-sm text-gray-900">${NUM_FMT.format(eng)}</td>`;
        tbody.appendChild(tr);
    });
    const tfoot=document.getElementById('pivot-adv-foot');
    if(tfoot){
        tfoot.innerHTML=
            `<tr class="bg-gray-50 font-medium">`+
            `<td class="px-2 py-2">Tổng cộng</td>`+
            `<td class="px-2 py-2">${VND_FMT.format(totalSpend)}</td>`+
            `<td class="px-2 py-2">${NUM_FMT.format(totalReach)}</td>`+
            `<td class="px-2 py-2">${NUM_FMT.format(totalImpr)}</td>`+
            `<td class="px-2 py-2">${NUM_FMT.format(totalNew)}</td>`+
            `<td class="px-2 py-2">${VND_FMT.format(totalNew>0?totalSpend/totalNew:0)}</td>`+
            `<td class="px-2 py-2">${VND_FMT.format(totalPV)}</td>`+
            `<td class="px-2 py-2">${NUM_FMT.format(totalEng)}</td>`+
            `</tr>`;
    }
}

function renderPivotAdvancedLine(rows){
    const c=document.getElementById('pivot-adv-line');
    if(!c) return;
    const ctx=c.getContext('2d');
    if(window.charts && charts.pivotLine){ charts.pivotLine.destroy(); }
    const labels=[]; const spend=[]; const impr=[]; const eng=[];
    rows.forEach(day=>{
        labels.push(new Date(day.date_start||day.date).toLocaleDateString('vi-VN'));
        spend.push(safeFloat(day.spend));
        impr.push(safeInt(day.impressions));
        eng.push(safeInt(day.post_engagement||0));
    });
    window.charts = window.charts || {};
    charts.pivotLine = new Chart(ctx,{
        type:'line',
        data:{
            labels,
            datasets:[
                {label:'Chi tiêu', data:spend, borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,0.2)', yAxisID:'y1'},
                {label:'Impressions', data:impr, borderColor:'#3b82f6', backgroundColor:'rgba(59,130,246,0.2)', yAxisID:'y2'},
                {label:'Engagement', data:eng, borderColor:'#10b981', backgroundColor:'rgba(16,185,129,0.2)', yAxisID:'y2'}
            ]
        },
        options:{
            responsive:true, maintainAspectRatio:false,
            scales:{
                y1:{position:'left', beginAtZero:true, title:{display:true,text:'VND'}},
                y2:{position:'right', beginAtZero:true, grid:{drawOnChartArea:false}}
            }
        }
    });
}

// Optional: pies require demographic breakdown per campaign; left as placeholders to be wired later
async function fetchPivotAdvancedBreakdowns(){
    try{
        const preset=document.getElementById('daily-date-preset')?.value||'last_30d';
        const res=await fetch(`/api/daily-breakdowns?date_preset=${encodeURIComponent(preset)}`);
        const d=await res.json();
        if(d.error) return;
        renderPivotAdvancedPies('pivot-adv-pie-gender', d.gender);
        renderPivotAdvancedPies('pivot-adv-pie-age', d.age);
        renderPivotAdvancedPies('pivot-adv-pie-geo', d.country);
        renderPivotAdvancedDistTable('pivot-adv-gender-tb', d.gender, 'Gender');
        renderPivotAdvancedDistTable('pivot-adv-age-tb', d.age, 'Age Range');
        renderPivotAdvancedDistTable('pivot-adv-geo-tb', d.country, 'Region');
    }catch(e){ console.error('breakdowns error', e); }
}

function renderPivotAdvancedPies(canvasId, bucket){
    const c=document.getElementById(canvasId); if(!c) return;
    const labels=Object.keys(bucket||{});
    const values=labels.map(k=> parseInt((bucket[k]?.impressions)||0) );
    const ctx=c.getContext('2d');
    if(!window.charts) window.charts={};
    charts[canvasId] && charts[canvasId].destroy();
    charts[canvasId] = new Chart(ctx,{
        type:'doughnut',
        data:{ labels, datasets:[{ data:values, backgroundColor:['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4','#84cc16'] }] },
        options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{position:'bottom'} } }
    });
}

function renderPivotAdvancedDistTable(tbodyId, bucket, firstCol){
    const tbody=document.getElementById(tbodyId); if(!tbody) return;
    tbody.innerHTML='';
    let totI=0, totC=0, totNew=0;
    Object.entries(bucket||{}).forEach(([k,v])=>{
        const tr=document.createElement('tr');
        tr.innerHTML=
          `<td class="px-2 py-2">${k}</td>`+
          `<td class="px-2 py-2">${NUM_FMT.format(parseInt(v.impressions||0))}</td>`+
          `<td class="px-2 py-2">${NUM_FMT.format(parseInt(v.clicks||0))}</td>`+
          `<td class="px-2 py-2">${v.ctr?.toFixed? v.ctr.toFixed(2): '0.00'}%</td>`+
          `<td class="px-2 py-2">${NUM_FMT.format(parseInt(v.new_messages||0))}</td>`;
        tbody.appendChild(tr);
        totI+=parseInt(v.impressions||0); totC+=parseInt(v.clicks||0); totNew+=parseInt(v.new_messages||0);
    });
    const footId=tbodyId+'-foot';
    const tfoot=document.getElementById(footId);
    if(tfoot){
        const ctr = (totC/Math.max(totI,1))*100.0;
        tfoot.innerHTML=`<tr class="bg-gray-50 font-medium"><td class="px-2 py-2">Tổng cộng</td><td class="px-2 py-2">${NUM_FMT.format(totI)}</td><td class="px-2 py-2">${NUM_FMT.format(totC)}</td><td class="px-2 py-2">${ctr.toFixed(2)}%</td><td class="px-2 py-2">${NUM_FMT.format(totNew)}</td></tr>`;
    }
}


