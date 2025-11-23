import React from 'react'
import DeviceCard from './DeviceCard'

export default function DeviceList({devices, loading}){
  if(loading) return <div className='small'>Loading devices...</div>
  if(!devices || devices.length === 0) return <div className='small'>No devices found</div>
  return (
    <div className='grid'>
      {devices.map(d=> (
        <div key={d.id} className='card'>
          <DeviceCard device={d} />
        </div>
      ))}
    </div>
  )
}
