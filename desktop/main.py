from flexx import flx

class Login(flx.Widget):

    CSS = """
    .flx-Login {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    """

    def init(self):
        flx.Label(text = 'Welcome to coffee talk!')
        self.name_input = flx.LineEdit()
        self.login_button = flx.Button(text = 'Log in')
        self.name_label = flx.Label(text = '')

    @flx.reaction('login_button.pointer_click')
    def _login_button_clicked(self):
        is_user_valid = self.validate_users(self.name_input.text)
        
        if not is_user_valid:
            self.name_label.set_text("User not authorized!")
        else:
            self.name_label.set_text('Welcome: ' + self.name_input.text)
            
    def validate_users(self, user_name):
        valid_users = ['Emil', 'Emilie', 'Hanne', 'Jonatan', 'Sebastian']

        return bool([ele for ele in valid_users if(ele in user_name)])

if __name__ == '__main__':
    flx.launch(Login)
    flx.run()
