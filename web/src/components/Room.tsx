import React, { ReactElement } from 'react'
import './Room.css'

export default function Room({roomName}: {roomName: string}): ReactElement {
    return (
        <div className='room-container'>
            <h2>{roomName}</h2>
        </div>
    )
}