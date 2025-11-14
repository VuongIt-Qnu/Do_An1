package com.example.demo.dto;

public class AuthResponse {

    private String message;
    private String token;
    private String email;
    private String fullName;
    private String role;
    private boolean success;

    public AuthResponse() {
    }

    public AuthResponse(String message, boolean success) {
        this.message = message;
        this.success = success;
    }

    // constructor đầy đủ
    public AuthResponse(String message, String token, String email,
                        String fullName, String role, boolean success) {
        this.message = message;
        this.token = token;
        this.email = email;
        this.fullName = fullName;
        this.role = role;
        this.success = success;
    }

    // getter/setter...

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }
}
