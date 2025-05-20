class Listener:
    def on_waiting_keyword(self):
        """Per impostare la pagina di ascolto della keyword"""
        pass

    def on_processing(self):
        """Per impostare la pagina di elaborazione"""
        pass

    def on_listening(self):
        """Per impostare la pagina di ascolto del brand"""
        pass

    def on_asking_confirm(self):
        """Per impostare la pagina di richiesta conferma"""
        pass

    def on_listening_confirm(self):
        """Per impostare la pagina di ascolto conferma"""
        pass

    def on_sent(self, brand):
        """Per impostare la pagina conferma dell'invio del brand"""
        pass