import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../environments/environment';

interface Message {
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'SmartKoach - AI Interview Coach';
  messages: Message[] = [];
  userMessage = '';
  selectedDomain = 'DSA';
  selectedDifficulty = 'Medium';
  isLoading = false;
  
  domains = ['DSA', 'ML', 'DBMS', 'OS', 'English', 'Botany', 'Math'];
  difficulties = ['Easy', 'Medium', 'Hard'];
  
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {
    // Add welcome message
    this.addAIMessage('Welcome to SmartKoach! I\'m your AI Interview Coach. Select a domain and difficulty level, then send a message to start your interview preparation.');
  }

  sendMessage() {
    if (!this.userMessage.trim() || this.isLoading) {
      return;
    }

    const message = this.userMessage.trim();
    this.userMessage = '';
    
    // Add user message to chat
    this.addUserMessage(message);
    
    // Show loading state
    this.isLoading = true;

    // Call backend API
    this.http.post<{ reply: string }>(`${this.apiUrl}/chat`, {
      message: message,
      domain: this.selectedDomain,
      difficulty: this.selectedDifficulty
    }).subscribe({
      next: (response) => {
        this.addAIMessage(response.reply);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error:', error);
        this.addAIMessage('Sorry, there was an error processing your request. Please check if the backend is running and try again.');
        this.isLoading = false;
      }
    });
  }

  resetChat() {
    this.http.post(`${this.apiUrl}/reset`, {}).subscribe({
      next: () => {
        this.messages = [];
        this.addAIMessage('Conversation reset. Let\'s start fresh! What would you like to practice?');
      },
      error: (error) => {
        console.error('Error resetting chat:', error);
      }
    });
  }

  private addUserMessage(text: string) {
    this.messages.push({
      text,
      sender: 'user',
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  private addAIMessage(text: string) {
    this.messages.push({
      text,
      sender: 'ai',
      timestamp: new Date()
    });
    this.scrollToBottom();
  }

  private scrollToBottom() {
    setTimeout(() => {
      const chatContainer = document.querySelector('.chat-messages');
      if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }
    }, 100);
  }

  onKeyPress(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }
}
