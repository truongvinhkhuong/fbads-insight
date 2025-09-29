// JavaScript for Chatbot functionality

function initializeChatbot(){
    const toggleBtn=document.getElementById('chatbot-toggle');
    const container=document.getElementById('chatbot-container');
    const input=document.getElementById('chatbot-input');
    const sendBtn=document.getElementById('chatbot-send');
    toggleBtn.addEventListener('click',()=>{ 
        container.style.display=container.style.display==='none'?'block':'none'; 
    });
    
    function buildContext(){
        // Lấy dữ liệu đang có trong trang làm context cho bot
        const ctx={
            campaigns_count: adsData?.campaigns?.length||0,
            // Thêm dữ liệu daily gần nhất của biểu đồ nếu có
        };
        return ctx;
    }
    
    function sendMessage(q){ 
        if(!q){ q=input.value.trim(); } 
        if(!q) return; 
        addMessage(q,'user'); 
        input.value=''; 
        addMessage('Đang xử lý...','bot'); 
        fetch('/api/ask',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                question:q,
                context:buildContext()
            })
        })
        .then(r=>r.json())
        .then(d=>{ 
            removeLastMessage(); 
            addMessage(d.error?('Lỗi: '+d.error):d.answer,'bot');
        })
        .catch(()=>{ 
            removeLastMessage(); 
            addMessage('Lỗi kết nối.','bot');
        }); 
    }
    
    sendBtn.addEventListener('click',sendMessage); 
    input.addEventListener('keypress',e=>{ 
        if(e.key==='Enter') sendMessage(); 
    });
    
    // Nút gợi ý nhanh
    document.querySelectorAll('[data-suggest]').forEach(btn=>{ 
        btn.addEventListener('click',()=> sendMessage(btn.getAttribute('data-suggest'))); 
    });
}

function addMessage(text,type){ 
    const box=document.getElementById('chatbot-messages'); 
    const div=document.createElement('div'); 
    div.className=`message ${type}-message`; 
    div.textContent=text; 
    box.appendChild(div); 
    box.scrollTop=box.scrollHeight; 
}

function removeLastMessage(){ 
    const box=document.getElementById('chatbot-messages'); 
    const msgs=box.querySelectorAll('.message'); 
    if(msgs.length>0) msgs[msgs.length-1].remove(); 
}
