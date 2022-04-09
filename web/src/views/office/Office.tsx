import React, { ReactElement, useState } from 'react'
import { useLocation } from 'react-router-dom'
import './Office.css'

export default function Office(): ReactElement {
    const { state }: {state: any} = useLocation()

    const rooms = ["Cantine", "Coffe", "Ping-pong", "Lounge"]

    return (
        <div>
            <h1 className='office-info'>Sales AS, Oslovegen 1</h1>
        </div>
    )
}