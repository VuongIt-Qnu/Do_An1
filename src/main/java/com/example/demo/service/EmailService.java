package com.example.demo.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.stereotype.Service;

@Service
public class EmailService {
    
    private final JavaMailSender mailSender;
    
    @Value("${spring.mail.username}")
    private String fromEmail;
    
    @Value("${app.reset-password.url:http://localhost:8080/api/auth/reset-password?token=}")
    private String resetPasswordUrl;
    
    public EmailService(JavaMailSender mailSender) {
        this.mailSender = mailSender;
    }
    
    public void sendPasswordResetEmail(String toEmail, String resetToken) {
        try {
            SimpleMailMessage message = new SimpleMailMessage();
            message.setFrom(fromEmail);
            message.setTo(toEmail);
            message.setSubject("Đặt lại mật khẩu - Hệ thống quản lý khách sạn");
            
            String resetLink = resetPasswordUrl + resetToken;
            String emailBody = "Xin chào,\n\n" +
                    "Bạn đã yêu cầu đặt lại mật khẩu cho tài khoản của mình.\n\n" +
                    "Vui lòng click vào link sau để đặt lại mật khẩu:\n" +
                    resetLink + "\n\n" +
                    "Link này sẽ hết hạn sau 1 giờ.\n\n" +
                    "Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.\n\n" +
                    "Trân trọng,\n" +
                    "Hệ thống quản lý khách sạn";
            
            message.setText(emailBody);
            
            mailSender.send(message);
        } catch (Exception e) {
            // Log error but don't throw exception to avoid revealing email issues
            System.err.println("Error sending email: " + e.getMessage());
        }
    }
}

