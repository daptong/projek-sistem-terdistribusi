import React, {useState} from 'react'
import { controlDevice } from '../services/api'

export default function GateControl({device}){
  const [busy, setBusy] = useState(false)
  const [token, setToken] = useState('')

  const act = async (action)=>{
    setBusy(true)
    try{
      const params = action === 'open' ? { auth_token: token } : {}
      await controlDevice(device.id, device.type, action, params)
    }catch(e){
      console.error(e)
      alert('Error sending gate command')
    }finally{
      setBusy(false)
    }
  }

  return (
    <div>
      <div style={{display:'flex',gap:8,alignItems:'center'}}>
        <input placeholder='auth token' value={token} onChange={e=>setToken(e.target.value)} style={{padding:6,borderRadius:6,border:'1px solid #ddd'}} />
      </div>
      <div className='device-actions' style={{marginTop:8}}>
        <button className='btn' onClick={()=>act('open')} disabled={busy}>Open Gate</button>
        <button className='btn secondary' onClick={()=>act('close')} disabled={busy}>Close Gate</button>
      </div>
    </div>
  )
}
