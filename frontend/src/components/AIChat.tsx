// src/components/AIChat.tsx (Corrected)
import React, { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send, LogIn, MessageSquare, Menu, BarChart2, PlusCircle, Crown } from "lucide-react";
import { auth, db } from "@/lib/firebase";
import { doc, setDoc, getDoc, collection, addDoc, orderBy, onSnapshot, serverTimestamp, query } from "firebase/firestore";
import { onAuthStateChanged, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { SidebarProvider } from "@/components/ui/sidebar";
import { ChartContainer } from "@/components/ui/chart";
import { useNavigate } from 'react-router-dom';
import { useUser } from "@/contexts/UserContext";

// INTERFACES
interface Message {
  id: string;
  type: "ai" | "user";
  content: string;
  timestamp: Date;
  suggestions?: string[];
  showChart?: boolean;
}

interface ChatMetadata {
  id: string;
  title: string;
  createdAt: Date;
  lastActivity: Date;
}

const FREE_TRIAL_LIMIT = 3;

// COMPONENT
export const AIChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [freeTrialCount, setFreeTrialCount] = useState(0);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // State Management Refactor:
  // chatSessions is the single source of truth for all conversation histories.
  const [chatSessions, setChatSessions] = useState<Record<string, Message[]>>({});
  const [chatMetadata, setChatMetadata] = useState<ChatMetadata[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  const chatScrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const navigate = useNavigate();
  const { isPro } = useUser();

  // WELCOME MESSAGE
  const getWelcomeMessage = useCallback((): Message => ({
    id: "welcome",
    type: "ai",
    content: "Hello! I'm your FinSight AI advisor. Ask me anything about your investments or taxes.",
    timestamp: new Date(),
  }), []);
  
  // CHAT TITLE GENERATOR
  const generateChatTitle = useCallback((content: string): string => {
    const words = content.trim().split(" ");
    return words.slice(0, 5).join(" ") + (words.length > 5 ? "..." : "");
  }, []);

  // EFFECT: Handle Authentication State
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      setAuthLoading(false);
      if (firebaseUser) {
        setShowAuthPrompt(false);
        const userDocRef = doc(db, "users", firebaseUser.uid);
        const userDoc = await getDoc(userDocRef);
        setFreeTrialCount(userDoc.exists() ? userDoc.data().freeTrialCount || 0 : 0);
      }
    });
    return () => unsubscribe();
  }, []);

  // EFFECT: Load Chat History (Metadata)
  useEffect(() => {
    if (authLoading || !user) {
      // If not authenticated, set up a default guest session
      if (!authLoading && !user && !activeChatId) {
        const defaultChatId = "guest-chat";
        setActiveChatId(defaultChatId);
        setChatSessions({ [defaultChatId]: [getWelcomeMessage()] });
      }
      return;
    }

    const chatsCollectionRef = collection(db, "users", user.uid, "chats");
    const q = query(chatsCollectionRef, orderBy("lastActivity", "desc"));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const loadedMetadata: ChatMetadata[] = snapshot.docs.map(doc => ({
        id: doc.id,
        title: doc.data().title || "Untitled Chat",
        createdAt: doc.data().createdAt?.toDate() || new Date(),
        lastActivity: doc.data().lastActivity?.toDate() || new Date(),
      }));
      setChatMetadata(loadedMetadata);

      // If there's no active chat, set it to the most recent one, or create a new one.
      if (!activeChatId || !loadedMetadata.some(chat => chat.id === activeChatId)) {
        if (loadedMetadata.length > 0) {
          setActiveChatId(loadedMetadata[0].id);
        } else {
          handleNewChat();
        }
      }
    }, (error) => {
      console.error("Error fetching chat metadata:", error);
      toast({ title: "Error loading chats", description: "Could not load previous conversations.", variant: "destructive" });
    });

    return () => unsubscribe();
  }, [user, authLoading]);

  // EFFECT: Load Messages for the Active Chat
  useEffect(() => {
    if (authLoading || !user || !activeChatId) return;

    // Skip Firestore for the default guest chat
    if (activeChatId === 'guest-chat') return;

    const messagesCollectionRef = collection(db, "users", user.uid, "chats", activeChatId, "messages");
    const q = query(messagesCollectionRef, orderBy("createdAt", "asc"));

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const loadedMessages: Message[] = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...(doc.data() as Omit<Message, 'id' | 'timestamp'>),
        timestamp: doc.data().createdAt?.toDate() || new Date(),
      }));
      
      setChatSessions(prev => ({
        ...prev,
        [activeChatId]: loadedMessages.length > 0 ? loadedMessages : [getWelcomeMessage()],
      }));
    }, (error) => {
      console.error(`Error fetching messages for chat ${activeChatId}:`, error);
      toast({ title: "Error loading chat history", description: "Could not load messages for this conversation.", variant: "destructive" });
    });

    return () => unsubscribe();
  }, [user, activeChatId, authLoading]);

  // EFFECT: Update displayed messages when active chat or sessions change
  useEffect(() => {
    if (!activeChatId) {
        setMessages([getWelcomeMessage()]);
        return;
    };
    setMessages(chatSessions[activeChatId] || [getWelcomeMessage()]);
  }, [activeChatId, chatSessions, getWelcomeMessage]);
  
  // EFFECT: Auto-scroll to bottom
  useEffect(() => {
    if (isAtBottom && chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [messages, isAtBottom]);

  // HANDLER: Manual scroll tracking
  const handleChatScroll = () => {
    const el = chatScrollRef.current;
    if (!el) return;
    setIsAtBottom(el.scrollHeight - el.scrollTop - el.clientHeight < 50);
  };

  // HANDLER: Start a new conversation
  const handleNewChat = async () => {
    setInputValue("");
    setIsTyping(false);
    
    const newChatId = `chat-${Date.now()}`;
    const welcomeMsg = getWelcomeMessage();

    setChatSessions(prev => ({ ...prev, [newChatId]: [welcomeMsg] }));
    setActiveChatId(newChatId);

    if (user) {
      const chatDocRef = doc(db, "users", user.uid, "chats", newChatId);
      await setDoc(chatDocRef, {
        title: "New Chat",
        createdAt: serverTimestamp(),
        lastActivity: serverTimestamp(),
      });
      await addDoc(collection(chatDocRef, "messages"), { ...welcomeMsg, createdAt: serverTimestamp() });
    }

    inputRef.current?.focus();
  };
  
  // HANDLER: Send a message
  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;
    if (!user && freeTrialCount >= FREE_TRIAL_LIMIT) {
      setShowAuthPrompt(true);
      return;
    }

    let currentChatId = activeChatId;
    if (!currentChatId || (messages.length === 1 && messages[0].id === 'welcome')) {
      // Create a new chat if it's the first message
      currentChatId = `chat-${Date.now()}`;
      setActiveChatId(currentChatId);
    }
    
    setInputValue("");
    setIsTyping(true);

    const userMsg: Message = { id: Date.now().toString(), type: "user", content, timestamp: new Date() };
    
    // Immediately update the UI
    setChatSessions(prev => ({
        ...prev,
        [currentChatId!]: [...(prev[currentChatId!] || []), userMsg]
    }));

    // Persist user message and update chat metadata if logged in
    if (user) {
      const chatDocRef = doc(db, "users", user.uid, "chats", currentChatId!);
      const messagesRef = collection(chatDocRef, "messages");
      
      const isFirstUserMessage = messages.filter(m => m.type === 'user').length === 0;
      if (isFirstUserMessage) {
        await setDoc(chatDocRef, { title: generateChatTitle(content), lastActivity: serverTimestamp() }, { merge: true });
        // Add welcome message to new firestore chat
        await addDoc(messagesRef, { ...getWelcomeMessage(), createdAt: serverTimestamp() });
      } else {
        await setDoc(chatDocRef, { lastActivity: serverTimestamp() }, { merge: true });
      }
      await addDoc(messagesRef, { ...userMsg, createdAt: serverTimestamp() });
      
      // Increment free trial count
      const userDocRef = doc(db, "users", user.uid);
      await setDoc(userDocRef, { freeTrialCount: freeTrialCount + 1 }, { merge: true });
    } else {
      setFreeTrialCount(c => c + 1);
    }

    // Call backend for AI response
    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content, user_id: user?.uid || "guest_user", chat_id: currentChatId }),
      });

      if (!res.ok) throw new Error(`Backend responded with status: ${res.status}`);
      
      const data = await res.json();
      
      // 1. Create the object for your local UI state (it's okay if it has undefined)
      const aiMsgForUI: Message = {
        id: (Date.now() + 1).toString(),
        type: "ai",
        content: data.response,
        timestamp: new Date(),
        suggestions: data.suggestions,
        showChart: data.showChart,
      };

      // 2. Create a clean payload for Firestore, only adding fields that exist
      const firestorePayload: any = {
          type: "ai",
          content: data.response,
          createdAt: serverTimestamp(),
      };

      if (data.suggestions) {
          firestorePayload.suggestions = data.suggestions;
      }
      // Check for boolean 'false' as a valid value
      if (typeof data.showChart !== 'undefined') {
          firestorePayload.showChart = data.showChart;
      }

      if (user) {
        // 3. Use the clean payload for the database operation
        await addDoc(collection(db, "users", user.uid, "chats", currentChatId!, "messages"), firestorePayload);
      }
      
      // 4. Update your local state with the full UI object
      setChatSessions(prev => ({ ...prev, [currentChatId!]: [...(prev[currentChatId!] || []), aiMsgForUI] }));

    } catch (err) {
      console.error("Backend call failed:", err);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: "I'm having trouble connecting to my brain right now. Please make sure the backend server is running and try again.",
        timestamp: new Date(),
      };
      setChatSessions(prev => ({ ...prev, [currentChatId!]: [...(prev[currentChatId!] || []), errorMsg] }));
    } finally {
      setIsTyping(false);
      if (!user && freeTrialCount + 1 >= FREE_TRIAL_LIMIT) {
        setTimeout(() => setShowAuthPrompt(true), 1000);
      }
    }
  };

  // HANDLER: Click on suggestion badge
  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  // HANDLER: Sign in with Google
  const handleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const userDocRef = doc(db, "users", result.user.uid);
      const userDoc = await getDoc(userDocRef);

      if (!userDoc.exists()) {
        await setDoc(userDocRef, {
          email: result.user.email,
          displayName: result.user.displayName,
          photoURL: result.user.photoURL,
          lastSignIn: serverTimestamp(),
          createdAt: serverTimestamp(),
          isPro: false,
          freeTrialCount: 0,
        });
        toast({ title: "Welcome to FinSight!", description: "Your account has been created." });
      } else {
        await setDoc(userDocRef, { lastSignIn: serverTimestamp() }, { merge: true });
        toast({ title: "Welcome back!", description: "Signed in successfully." });
      }
      // Reset guest chat state after login
      setActiveChatId(null);
      setChatSessions({});

    } catch (error: any) {
      toast({ title: "Sign In Failed", description: error.message, variant: "destructive" });
    }
  };

  // HANDLER: Go to Pro subscription page
  const handleGoProClick = () => {
    navigate("/pro-subscription");
  };

  // Check if user should be redirected to Pro chat
  useEffect(() => {
    if (user && isPro) {
      navigate("/pro-ai-chat", { replace: true });
    }
  }, [user, isPro, navigate]);

  const isInputDisabled = isTyping || (!user && freeTrialCount >= FREE_TRIAL_LIMIT);

  // JSX RETURN
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-gradient-to-br from-background to-zinc-900">
        {/* Desktop Sidebar */}
        <div className="hidden md:flex flex-col" style={{ width: 250 }}>
          {sidebarOpen && (
            <div className="w-full flex-shrink-0 border-r border-border bg-card/90 shadow-lg flex flex-col h-full">
              <div className="flex items-center justify-between font-bold text-base px-4 py-3 border-b border-border">
                <span className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-primary" />
                  FinSight AI
                </span>
                <button className="p-1 rounded-full hover:bg-accent/50" onClick={() => setSidebarOpen(false)} aria-label="Close sidebar">
                  <Menu className="w-6 h-6 text-muted-foreground" />
                </button>
              </div>
              {user && (
                <div className="flex items-center gap-3 px-4 py-3 border-b border-border/60 bg-background/80">
                  <img src={user.photoURL} alt="User avatar" className="w-8 h-8 rounded-full border border-border" />
                  <span className="font-medium text-sm text-foreground truncate">{user.displayName || user.email}</span>
                </div>
              )}
              <div className="flex-1 overflow-y-auto">
                <nav className="flex flex-col gap-1 px-2 py-2">
                  <button className="flex items-center gap-2 text-left py-2 px-3 rounded-lg hover:bg-primary/10 font-medium transition group text-sm" onClick={handleNewChat}>
                    <PlusCircle className="w-4 h-4 text-primary group-hover:scale-110 transition" />
                    New Chat
                  </button>
                </nav>
                <div className="px-2"><div className="my-1 border-t border-border/60" /></div>
                <div className="px-2 pb-2">
                  <div className="text-xs text-muted-foreground font-semibold mb-1 mt-1 px-1">Previous Chats</div>
                  <div className="flex flex-col gap-0.5">
                    {chatMetadata.length === 0 && user ? (
                      <span className="text-sm text-muted-foreground px-2 py-2">No previous chats.</span>
                    ) : (
                      chatMetadata.map(chat => (
                        <button
                          key={chat.id}
                          onClick={() => setActiveChatId(chat.id)}
                          className={`flex items-start gap-2 px-2 py-2 rounded-lg transition text-left w-full border-l-4 group text-sm ${
                            activeChatId === chat.id
                              ? 'bg-primary/10 border-primary shadow-sm'
                              : 'bg-transparent border-transparent hover:bg-accent/20 hover:border-primary/60'
                          }`}
                        >
                          <Bot className="w-4 h-4 mt-0.5 text-muted-foreground group-hover:text-primary transition flex-shrink-0" />
                          <span className="truncate text-sm text-foreground group-hover:text-primary min-w-0">
                            {chat.title}
                          </span>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
          {!sidebarOpen && (
            <button className="p-2 rounded-lg hover:bg-accent/50" onClick={() => setSidebarOpen(true)} aria-label="Open sidebar">
              <Menu className="w-6 h-6 text-primary" />
            </button>
          )}
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col h-full w-full min-h-0 px-0 md:px-8 py-2 md:py-6">
          <div className="relative flex flex-col items-center justify-center gap-1 py-2 px-4 border-b border-border/20">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h3 className="font-bold text-lg text-foreground">FinSight AI</h3>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-500 font-medium">Online</span>
            </div>
            <div className="absolute top-2 right-4 md:right-8">
              <Button
                variant="outline"
                className="bg-gradient-to-r from-amber-400 to-amber-600 hover:from-amber-500 hover:to-amber-700 text-white flex items-center gap-2 rounded-full px-4 py-2 text-sm shadow-md transition-all duration-200 hover:scale-[1.02]"
                onClick={handleGoProClick}
              >
                <Crown className="w-4 h-4 fill-white" />
                Go Pro
              </Button>
            </div>
          </div>

          <div className="flex-1 flex flex-col min-h-0">
            <div
              className="flex-1 flex flex-col gap-1 px-2 md:px-6 py-1 overflow-y-auto w-full"
              ref={chatScrollRef}
              style={{scrollBehavior: 'smooth'}}
              onScroll={handleChatScroll}
            >
              <div className="w-full">
                {messages.length <= 1 && !isTyping ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                      <MessageSquare className="w-12 h-12 mb-4 text-primary/50" />
                      <p className="text-lg font-semibold">Start a new conversation</p>
                      <p className="text-sm">Type a message below to begin.</p>
                    </div>
                ) : (
                    messages.map((message, idx) => (
                      <div
                        key={message.id}
                        className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} items-end animate-fade-in mb-1 group`}
                      >
                        {message.type === "ai" && (
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center mr-2 flex-shrink-0 shadow-md">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div
                          className={`rounded-2xl px-4 py-2 text-sm shadow-lg break-words relative transition-all duration-200 ${
                            message.type === "ai"
                              ? "bg-gradient-to-br from-background/90 to-accent/10 text-foreground border border-border/30"
                              : "bg-primary text-primary-foreground"
                          }`}
                          style={{ maxWidth: '90%' }}
                        >
                          {message.content}
                          <span className="block text-[10px] text-muted-foreground mt-1 text-right opacity-80 select-none">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          {message.type === "ai" && message.suggestions && (
                            <div className="flex flex-wrap gap-2 mt-2 pt-2 border-t border-border/50">
                              {message.suggestions.map((suggestion, sIdx) => (
                                <Badge
                                  key={sIdx}
                                  variant="secondary"
                                  className="cursor-pointer hover:bg-accent/80 transition-colors text-xs py-1 px-2 rounded-full"
                                  onClick={() => handleSuggestionClick(suggestion)}
                                >
                                  {suggestion}
                                </Badge>
                              ))}
                            </div>
                          )}
                          {message.type === "ai" && message.showChart && (
                            <div className="mt-4">
                              <ChartContainer config={{}} className="aspect-auto h-[250px] w-full">
                                <div className="flex items-center justify-center h-full border border-dashed rounded-lg bg-background/50 text-muted-foreground">
                                  <BarChart2 className="w-8 h-8 mr-2" />
                                  <span>Chart Placeholder</span>
                                </div>
                              </ChartContainer>
                            </div>
                          )}
                        </div>
                        {message.type === "user" && (
                          <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center ml-2 flex-shrink-0 shadow-md">
                            {user?.photoURL ? (
                              <img src={user.photoURL} alt="User avatar" className="w-full h-full rounded-full" />
                            ) : (
                              <User className="w-4 h-4 text-muted-foreground" />
                            )}
                          </div>
                        )}
                      </div>
                    ))
                )}
                {isTyping && (
                  <div className="flex gap-2 items-center animate-fade-in mb-1">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 shadow-md">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-background/90 border border-border/50 px-3 py-2 rounded-2xl flex items-center gap-1 shadow-md">
                      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce" />
                      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                      <div className="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="border-t border-border/20 bg-background/95 sticky bottom-0 z-10 shadow-2xl">
              {showAuthPrompt && (
                <div className="bg-orange-500/10 border border-orange-500/30 text-orange-400 text-sm p-3 mx-3 md:mx-6 mb-2 rounded-lg flex items-center justify-between shadow-md">
                  <span>Your free trial has ended. Please sign in or Go Pro for unlimited access!</span>
                  <div className="flex gap-2">
                    <Button onClick={handleSignIn} className="ml-4 bg-orange-500 hover:bg-orange-600 text-white flex items-center gap-2 rounded-full px-4 py-2" size="sm">
                      <LogIn className="w-4 h-4" /> Sign In
                    </Button>
                    <Button onClick={handleGoProClick} className="bg-amber-500 hover:bg-amber-600 text-white flex items-center gap-2 rounded-full px-4 py-2" size="sm">
                      <Crown className="w-4 h-4 fill-white" /> Go Pro
                    </Button>
                  </div>
                </div>
              )}
              <form
                className="flex items-center gap-3 w-full px-3 md:px-6 py-3 rounded-xl bg-background/95 shadow-lg mt-2"
                onSubmit={e => { e.preventDefault(); handleSendMessage(inputValue); }}
              >
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  placeholder="Ask FinSight AI anything..."
                  className="flex-1 min-h-[44px] pr-12 text-base shadow-sm focus-visible:ring-offset-0 focus-visible:ring-primary/50"
                  disabled={isInputDisabled}
                  autoFocus
                />
                <Button type="submit" size="icon" className="w-10 h-10 rounded-full bg-primary hover:bg-primary/90 absolute right-6 md:right-9" disabled={isInputDisabled}>
                  <Send className="w-5 h-5" />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
};