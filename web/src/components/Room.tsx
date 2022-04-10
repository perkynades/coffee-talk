import { Button, Modal } from 'antd'
import React, { ReactElement, useState } from 'react'
import './Room.css'

export default function Room({roomName}: {roomName: string}): ReactElement {
    const [modalVisible, setModalVisible] = useState<boolean>(false)
    
    const onModalOk = () => {
        
    }

    return (
        <div className='room-container'>
            <h2>{roomName}</h2>
            <div>
                <Button type='primary' onClick={() => setModalVisible(true)}>
                    Join {roomName} room
                </Button>
                <Modal
                    title={"Join " + roomName + "?"} 
                    visible={modalVisible}
                    onOk={onModalOk}
                    onCancel={() => setModalVisible(false)}
                >
                    <p>Do you want to join the {roomName.toLowerCase()} room?</p>
                </Modal>
            </div>
        </div>
    )
}