// JavaScript for breakdown functionality

async function fetchBreakdown(campaignId, kind){
    const preset=document.getElementById('date-preset')?.value||'last_30d';
    let q=`date_preset=${encodeURIComponent(preset)}`;
    if(preset==='custom'){
        const s=document.getElementById('since').value; 
        const u=document.getElementById('until').value;
        if(s&&u) q=`since=${encodeURIComponent(s)}&until=${encodeURIComponent(u)}`;
    }
    const url=`/api/campaign-breakdown?campaign_id=${encodeURIComponent(campaignId)}&kind=${kind}&${q}`;
    const res = await fetch(url);
    const data = await res.json();
    console.log('BREAKDOWN', kind, url, data);
    return data;
}

async function fetchAds(campaignId){
    const preset=document.getElementById('date-preset')?.value||'last_30d';
    let q=`date_preset=${encodeURIComponent(preset)}`;
    if(preset==='custom'){
        const s=document.getElementById('since').value; 
        const u=document.getElementById('until').value;
        if(s&&u) q=`since=${encodeURIComponent(s)}&until=${encodeURIComponent(u)}`;
    }
    const url=`/api/campaign-ads?campaign_id=${encodeURIComponent(campaignId)}&${q}`;
    const res = await fetch(url);
    const data = await res.json();
    console.log('ADS', url, data);
    return data;
}

function mapPlacementLabel(p){
    const m={
        'facebook:feed':'Facebook News Feed',
        'facebook:facebook_profile_feed':'Feed Profile',
        'facebook:video_feeds':'Video Feed',
        'facebook:story':'Stories',
        'instagram:stream':'Feed',
        'instagram:story':'Stories',
        'instagram:reels':'Reels',
        'audience_network:classic':'Audience Network',
        'messenger:inbox':'Inbox',
        'messenger:story':'Stories'
    };
    if(!p) return 'Unknown';
    const key=p.toLowerCase();
    if(m[key]) return m[key];
    // try format like publisher:position
    const parts=key.split(':');
    if(parts.length===2){
        const prettyPub=parts[0]==='facebook'?'':parts[0]==='instagram'?'':parts[0]==='messenger'?'':parts[0]==='audience_network'?'Audience Network':parts[0];
        const pos=parts[1].replace(/_/g,' ');
        return `${prettyPub} ${pos.charAt(0).toUpperCase()+pos.slice(1)}`;
    }
    return p;
}

function renderBreakdown(kind, rows){
    const ctx = document.getElementById('breakdownChart').getContext('2d');
    charts.breakdown && charts.breakdown.destroy();
    let labels=[], values=[];
    const keyMap={placement:'placement',age_gender:r=>`${r.age||''}/${r.gender||''}`,country:'country'};
    rows.forEach(r=>{ 
        const labelRaw = typeof keyMap[kind]==='function'?keyMap[kind](r):(r[keyMap[kind]]||'Unknown'); 
        const label = (kind==='placement')?mapPlacementLabel(labelRaw):labelRaw; 
        labels.push(label); 
        values.push(parseInt(r.impressions||0)); 
    })
    charts.breakdown = new Chart(ctx,{
        type:'bar',
        data:{
            labels,
            datasets:[{
                label:'Impressions',
                data:values,
                backgroundColor:'#247ba0'
            }]
        },
        options:{
            responsive:true,
            maintainAspectRatio:false,
            scales:{
                y:{beginAtZero:true}
            }
        }
    });
}

function renderCreatives(items){
    const box=document.getElementById('creative-list');
    box.innerHTML='';
    if(!items || !items.length){ 
        box.innerHTML='<div class="text-sm text-gray-500">Không có dữ liệu ads.</div>'; 
        return; 
    }
    const table=document.createElement('table');
    table.className='min-w-full divide-y divide-gray-200 text-sm';
    table.innerHTML=`<thead class="bg-gray-50"><tr><th class="px-3 py-2 text-left">Ad</th><th class="px-3 py-2 text-left">Status</th><th class="px-3 py-2 text-left">Impr</th><th class="px-3 py-2 text-left">Clicks</th><th class="px-3 py-2 text-left">Chi phí</th></tr></thead><tbody></tbody>`;
    const tb=table.querySelector('tbody');
    items.forEach(it=>{
        const ins=it.insights||{};
        const tr=document.createElement('tr');
        tr.innerHTML=`<td class="px-3 py-2">${it.ad.name||it.ad.id}</td><td class="px-3 py-2">${it.ad.status||''}</td><td class="px-3 py-2">${NUM_FMT.format(parseInt(ins.impressions||0))}</td><td class="px-3 py-2">${NUM_FMT.format(parseInt(ins.clicks||0))}</td><td class="px-3 py-2">${VND_FMT.format(parseFloat(ins.spend||0))}</td>`;
        tb.appendChild(tr);
    })
    box.appendChild(table);
}
