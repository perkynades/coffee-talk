import React, { ReactElement, useState } from 'react'
import { useLocation } from 'react-router-dom'
import Room from '../../components/Room'
import './Office.css'

export default function Office(): ReactElement {
    const { state }: {state: any} = useLocation()

    return (
        <div>
            <h1 className='office-info'>Sales AS, Oslovegen 1</h1>
            <div className='rooms-container'>
                <Room roomName='Cantine' />
                <Room roomName='Coffee' />
                <Room roomName='Ping-pong' />
                <Room roomName='Lounge' />
            </div>
        </div>
    )
}