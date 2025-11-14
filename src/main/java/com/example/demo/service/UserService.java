package com.example.demo.service;

import com.example.demo.dto.*;
import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import com.example.demo.util.JwtUtil;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtUtil jwtUtil;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, 
                      PasswordEncoder passwordEncoder,
                      AuthenticationManager authenticationManager,
                      JwtUtil jwtUtil,
                      EmailService emailService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.jwtUtil = jwtUtil;
        this.emailService = emailService;
    }
    
    @Transactional
    public AuthResponse register(SignUpRequest signUpRequest) {
        // Check if email already exists
        if (userRepository.existsByEmail(signUpRequest.getEmail())) {
            return new AuthResponse("Email đã được sử dụng", false);
        }

        // Create new user
        User user = new User();
        user.setFullName(signUpRequest.getFullName());
        user.setEmail(signUpRequest.getEmail());
        user.setPhoneNumber(signUpRequest.getPhoneNumber());
        user.setPassword(passwordEncoder.encode(signUpRequest.getPassword()));
        user.setRole("USER");
        user.setEnabled(true);

        userRepository.save(user);

        // Generate JWT token
        String token = jwtUtil.generateToken(user.getEmail());

        return new AuthResponse(
                "Đăng ký thành công",
                token,
                user.getEmail(),
                user.getFullName(),
                true
        );
    }

    public AuthResponse login(LoginRequest loginRequest) {
        try {
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    loginRequest.getEmail(),
                    loginRequest.getPassword()
                )
            );
            
            SecurityContextHolder.getContext().setAuthentication(authentication);
            
            User user = (User) authentication.getPrincipal();
            
            // Generate JWT token
            String token = jwtUtil.generateToken(user.getEmail());
            
            return new AuthResponse("Đăng nhập thành công", token, user.getEmail(), user.getFullName(), true);
        } catch (Exception e) {
            return new AuthResponse("Email hoặc mật khẩu không đúng", false);
        }
    }
    
    @Transactional
    public AuthResponse forgotPassword(ForgotPasswordRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElse(null);
        
        if (user == null) {
            // Don't reveal if email exists or not for security
            return new AuthResponse("Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu", true);
        }
        
        // Generate reset token
        String resetToken = UUID.randomUUID().toString();
        user.setResetToken(resetToken);
        user.setResetTokenExpiry(LocalDateTime.now().plusHours(1)); // Token valid for 1 hour
        
        userRepository.save(user);
        
        // Send email
        emailService.sendPasswordResetEmail(user.getEmail(), resetToken);
        
        return new AuthResponse("Nếu email tồn tại, chúng tôi đã gửi link đặt lại mật khẩu", true);
    }
    
    @Transactional
    public AuthResponse resetPassword(PasswordResetRequest request) {
        User user = userRepository.findByResetToken(request.getToken())
                .orElse(null);
        
        if (user == null) {
            return new AuthResponse("Token không hợp lệ hoặc đã hết hạn", false);
        }
        
        if (user.getResetTokenExpiry() == null || user.getResetTokenExpiry().isBefore(LocalDateTime.now())) {
            return new AuthResponse("Token đã hết hạn", false);
        }
        
        // Update password
        user.setPassword(passwordEncoder.encode(request.getNewPassword()));
        user.setResetToken(null);
        user.setResetTokenExpiry(null);
        
        userRepository.save(user);
        
        return new AuthResponse("Đặt lại mật khẩu thành công", true);
    }
}

