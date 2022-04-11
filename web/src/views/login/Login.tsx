import { Alert, Button, Form, Input } from 'antd'
import React, { ReactElement, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Login.css'

export default function Login(): ReactElement {

    const [userNotValid, setUserNotValid] = useState<boolean>(false)

    useEffect(() => {
        updateClientStateToPreLogin()
    }, [])

    const navigate = useNavigate()

    const validateUser = (username: string): boolean => {
        return ['Emil', 'Emilie', 'Hanne', 'Jonatan', 'Sebastian'].includes(username)
    }

    const onFormFinished = (values: any) => {
        if (validateUser(values.name)) {
            setUserNotValid(false)
            updateClientStateToLogin()
            navigate('/office-view', { state: values.name})
            
        } else {
            setUserNotValid(true)
        }
    }
    
    const updateClientStateToPreLogin = () => {
        // 1. Check if client is alreaddy connected, if not connect again
    }

    const updateClientStateToLogin = () => {
        // Emit things
    }

    return (
        <Form
            name='login'
            onFinish={onFormFinished}
            className="login-form"
        >
            <h1>Welcome to coffe-talk!</h1>
            <Form.Item
                label='Name'
                name='name'
            >
                <Input />
            </Form.Item>
            <Form.Item>
                <Button type="primary" htmlType='submit'>
                    Log in
                </Button>
            </Form.Item>
            {userNotValid && <Alert message="User not authenticated!" type="error" />}
        </Form>
    )
}