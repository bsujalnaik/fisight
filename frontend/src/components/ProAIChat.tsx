// src/components/ProAIChat.tsx (Pro Version)
import React, { useState, useRef, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bot, User, Send, MessageSquare, History, Settings as SettingsIcon, CircleDot, Menu, BarChart2, PlusCircle, Crown } from "lucide-react";
import { auth } from "@/lib/firebase";
import { db } from "@/lib/firebase";
import { doc, setDoc, getDoc, collection, addDoc, orderBy, onSnapshot, serverTimestamp, query } from "firebase/firestore";
import { onAuthStateChanged, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import {
  SidebarProvider,
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  SidebarInset
} from "@/components/ui/sidebar";
import { ChartContainer } from "@/components/ui/chart";
import { useUser } from "@/contexts/UserContext";
import { useNavigate } from 'react-router-dom';
// Remove Layout import since we'll use the shared layout

interface ProAIChatProps {
  tabActiveKey?: string;
}

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

export const ProAIChat = ({ tabActiveKey }: ProAIChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [user, setUser] = useState<any>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [showChart, setShowChart] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [chatSessions, setChatSessions] = useState<Record<string, Message[]>>({});
  const [chatMetadata, setChatMetadata] = useState<ChatMetadata[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();
  const navigate = useNavigate();
  // isPro from useUser can be used to gate this component via routing
  const { isPro } = useUser();

  // Ensure only Pro users can access this component
  useEffect(() => {
    if (user && !isPro) {
      navigate("/chat", { replace: true });
    }
  }, [user, isPro, navigate]);

  const getWelcomeMessage = useCallback((): Message => ({
    id: "welcome-pro",
    type: "ai",
    content: "Welcome to FinSight Pro! You have unlimited access to advanced analytics, real-time data, and priority support. How can I assist you today?",
    timestamp: new Date(),
  }), []);

  const generateChatTitle = useCallback((content: string): string => {
    const words = content.trim().split(" ");
    return words.slice(0, 6).join(" ") + (words.length > 6 ? "..." : "");
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      if (!firebaseUser) {
        // Pro users should be logged in. Redirect or show login prompt if needed.
        // For this component, we'll assume routing handles unauthorized access.
        setMessages([getWelcomeMessage()]);
      }
    });
    return () => unsubscribe();
  }, [getWelcomeMessage]);

  useEffect(() => {
    if (!user) return; // Don't fetch chats if there's no user

    const chatsCollectionRef = collection(db, "users", user.uid, "chats");
    const unsubscribe = onSnapshot(query(chatsCollectionRef, orderBy("lastActivity", "desc")), (snapshot) => {
      const loadedMetadata: ChatMetadata[] = snapshot.docs.map(doc => ({
        id: doc.id,
        title: doc.data().title || "Untitled Chat",
        createdAt: doc.data().createdAt?.toDate() || new Date(),
        lastActivity: doc.data().lastActivity?.toDate() || new Date(),
      }));
      setChatMetadata(loadedMetadata);

      if (activeChatId && loadedMetadata.some(chat => chat.id === activeChatId)) {
        // Active chat is still valid, no change needed
      } else if (loadedMetadata.length > 0) {
        setActiveChatId(loadedMetadata[0].id);
      } else {
        const newChatId = `chat-${Date.now()}`;
        handleNewChat(newChatId);
      }
    }, (error) => {
      console.error("Error fetching chat metadata:", error);
      toast({
        title: "Error loading chats",
        description: "Could not load your previous conversations.",
        variant: "destructive",
      });
    });
    return () => unsubscribe();
  }, [user, getWelcomeMessage]);

  useEffect(() => {
    if (!user || !activeChatId) {
      setMessages([]);
      return;
    }

    const messagesCollectionRef = collection(db, "users", user.uid, "chats", activeChatId, "messages");
    const unsubscribe = onSnapshot(query(messagesCollectionRef, orderBy("createdAt", "asc")), (snapshot) => {
      const loadedMessages: Message[] = snapshot.docs.map((doc) => {
        const data = doc.data();
        return {
          id: doc.id,
          type: data.type,
          content: data.content,
          timestamp: data.createdAt?.toDate ? data.createdAt.toDate() : new Date(),
          suggestions: data.suggestions || undefined,
          showChart: data.showChart || false,
        };
      });

      const finalMessages = loadedMessages.length > 0 ? loadedMessages : [getWelcomeMessage()];
      setMessages(finalMessages);
      setChatSessions(prev => ({
        ...prev,
        [activeChatId]: finalMessages,
      }));

    }, (error) => {
      console.error(`Error fetching messages for chat ${activeChatId}:`, error);
      toast({
        title: "Error loading chat history",
        description: "Could not load messages for this conversation.",
        variant: "destructive",
      });
    });

    return () => unsubscribe();
  }, [user, activeChatId, getWelcomeMessage]);

  useEffect(() => {
    const el = chatScrollRef.current;
    if (!el) return;
    if (isAtBottom) {
      el.scrollTop = el.scrollHeight;
    }
  }, [messages, isAtBottom]);

  const handleChatScroll = () => {
    const el = chatScrollRef.current;
    if (!el) return;
    setIsAtBottom(el.scrollHeight - el.scrollTop - el.clientHeight < 30);
  };

  const handleNewChat = async (newChatId?: string) => {
    if (!user) {
        toast({ title: "Authentication Required", description: "Please sign in to start a new chat.", variant: "destructive"});
        return;
    }
    const chatKey = newChatId || `chat-${Date.now()}`;
    const welcomeMsg = getWelcomeMessage();

    setInputValue("");
    setShowChart(false);
    setIsTyping(false);
    setMessages([welcomeMsg]);

    setChatSessions(prev => ({
      ...prev,
      [chatKey]: [welcomeMsg]
    }));
    setActiveChatId(chatKey);

    const chatDocRef = doc(db, "users", user.uid, "chats", chatKey);
    await setDoc(chatDocRef, {
      title: "New Pro Chat",
      createdAt: serverTimestamp(),
      lastActivity: serverTimestamp(),
    }, { merge: true });

    await addDoc(collection(chatDocRef, "messages"), {
      ...welcomeMsg,
      createdAt: serverTimestamp(),
    });

    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || !user) return; // Pro users must be logged in to send messages

    setInputValue("");
    setIsTyping(true);

    const userMsg: Message = {
      id: Date.now().toString(),
      type: "user",
      content,
      timestamp: new Date(),
    };

    let currentChatId = activeChatId;

    if (!currentChatId || (user && !chatSessions[currentChatId]?.length)) {
        let newTitle = generateChatTitle(content);
        let counter = 1;
        while (chatMetadata.some(chat => chat.title === newTitle)) {
            newTitle = `${generateChatTitle(content)} (${counter++})`;
        }
        currentChatId = `chat-${Date.now()}`;
        setActiveChatId(currentChatId);

        setChatSessions(prev => ({
            ...prev,
            [currentChatId]: [getWelcomeMessage(), userMsg]
        }));
        setMessages([getWelcomeMessage(), userMsg]);

        await setDoc(doc(db, "users", user.uid, "chats", currentChatId), {
            title: newTitle,
            createdAt: serverTimestamp(),
            lastActivity: serverTimestamp(),
        }, { merge: true });
        await addDoc(collection(db, "users", user.uid, "chats", currentChatId, "messages"), {
            ...getWelcomeMessage(),
            createdAt: serverTimestamp(),
        });

    } else {
        setMessages((prev) => [...prev, userMsg]);
        setChatSessions((prev) => ({
            ...prev,
            [currentChatId]: [...(prev[currentChatId] || []), userMsg],
        }));
    }

    const chatDocRef = doc(db, "users", user.uid, "chats", currentChatId!);
    await setDoc(chatDocRef, { lastActivity: serverTimestamp() }, { merge: true });

    await addDoc(collection(chatDocRef, "messages"), {
      ...userMsg,
      createdAt: serverTimestamp(),
    });

    const currentMessagesInActiveChat = chatSessions[currentChatId!] || [];
    const firstUserMessageSentInChat = currentMessagesInActiveChat.filter(msg => msg.type === 'user').length === 1;

    if (firstUserMessageSentInChat) {
         await setDoc(chatDocRef, {
             title: generateChatTitle(content),
         }, { merge: true });
    }

    try {
      const res = await fetch("http://localhost:8000/prochat", { // Using a potential 'pro' endpoint
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: content,
          user_id: user.uid, // user.uid is guaranteed here
          chat_id: currentChatId,
        }),
      });
      const data = await res.json();
      const aiMsg: Omit<Message, "id"> = {
        type: "ai",
        content: data.answer,
        timestamp: new Date(),
        suggestions: data.suggestions || [
            "Run advanced portfolio simulation",
            "Generate tax optimization report",
            "Analyze specific stock (e.g., AAPL)",
            "Show real-time market heat map",
        ],
        showChart: data.showChart || false,
      };

      const fullAiMsg: Message = { ...aiMsg, id: (Date.now() + 1).toString() };
      setMessages((prev) => [...prev, fullAiMsg]);
      setChatSessions((prev) => ({
        ...prev,
        [currentChatId!]: [...(prev[currentChatId!] || []), fullAiMsg],
      }));

      await setDoc(chatDocRef, { lastActivity: serverTimestamp() }, { merge: true });
      await addDoc(collection(chatDocRef, "messages"), {
        ...aiMsg,
        createdAt: serverTimestamp(),
      });

      if (aiMsg.showChart) setShowChart(true);
    } catch (err) {
      console.error("FastAPI call failed:", err);
      const aiMsg = generateAIResponse(content);
      const fullAiMsg: Message = { ...aiMsg, id: (Date.now() + 1).toString() };

      setMessages((prev) => [...prev, fullAiMsg]);
      setChatSessions((prev) => ({
        ...prev,
        [currentChatId!]: [...(prev[currentChatId!] || []), fullAiMsg],
      }));

      await setDoc(chatDocRef, { lastActivity: serverTimestamp() }, { merge: true });
      await addDoc(collection(chatDocRef, "messages"), {
        ...aiMsg,
        createdAt: serverTimestamp(),
      });
      if (aiMsg.showChart) setShowChart(true);
    } finally {
      setIsTyping(false);
    }
  };

  const generateAIResponse = (content: string): Omit<Message, "id"> => {
    if (content.toLowerCase().includes("chart")) {
      return {
        type: "ai",
        content: "Here is your advanced chart, rendered with real-time market data. You can customize the view and apply technical indicators.",
        timestamp: new Date(),
        showChart: true,
      };
    }
    return {
      type: "ai",
      content:
        "As a Pro user, I can provide a deep-dive analysis. Based on your portfolio and real-time market data, I suggest the following tax-loss harvesting opportunities...",
      timestamp: new Date(),
      suggestions: [
        "Run advanced portfolio simulation",
        "Generate tax optimization report",
        "Analyze specific stock (e.g., AAPL)",
        "Show real-time market heat map",
      ],
    };
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  const isInputDisabled = isTyping || !user;

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-gradient-to-br from-background to-zinc-900">
        {/* Pro Desktop Sidebar */}
        <div className="hidden md:flex flex-col" style={{ width: 250 }}>
          {sidebarOpen && (
            <div className="w-full flex-shrink-0 border-r border-border bg-card/90 shadow-lg flex flex-col h-full">
              <div className="flex items-center justify-between font-bold text-base px-4 py-3 border-b border-border">
                <span className="flex items-center gap-2 text-amber-500">
                  <Crown className="w-5 h-5 fill-amber-500" />
                  FinSight AI Pro
                </span>
                <button
                  className="p-1 rounded-full hover:bg-accent/50"
                  onClick={() => setSidebarOpen(false)}
                  aria-label="Close sidebar"
                >
                  <Menu className="w-6 h-6 text-muted-foreground" />
                </button>
              </div>
              {user && (
                <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-border/60 bg-background/80">
                  <div className="flex items-center gap-3 min-w-0">
                    <img src={user.photoURL} alt="User avatar" className="w-8 h-8 rounded-full border border-amber-500" />
                    <span className="font-medium text-sm text-foreground truncate">{user.displayName || user.email}</span>
                  </div>
                  <Crown className="w-5 h-5 text-amber-500 flex-shrink-0" />
                </div>
              )}
              <div className="flex-1 overflow-y-auto">
                <nav className="flex flex-col gap-1 px-2 py-2">
                  <button
                    className="flex items-center gap-2 text-left py-2 px-3 rounded-lg hover:bg-primary/10 font-medium transition group text-sm"
                    onClick={() => handleNewChat()}
                  >
                    <PlusCircle className="w-4 h-4 text-primary group-hover:scale-110 transition" />
                    New Chat
                  </button>
                </nav>
                <div className="px-2"><div className="my-1 border-t border-border/60" /></div>
                <div className="px-2 pb-2">
                  <div className="text-xs text-muted-foreground font-semibold mb-1 mt-1 px-1">Previous Chats</div>
                  <div className="flex flex-col gap-0.5">
                    {chatMetadata.length === 0 ? (
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
                          <Bot className="w-4 h-4 mt-0.5 text-muted-foreground group-hover:text-amber-500 transition flex-shrink-0" />
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
            <button
              className="p-2 rounded-lg hover:bg-accent/50"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <Menu className="w-6 h-6 text-primary" />
            </button>
          )}
        </div>

        {/* Mobile Sidebar (Pro) is omitted for brevity, but would follow the same style changes */}

        {/* Main Pro Chat Area */}
        <div className="flex-1 flex flex-col h-full w-full min-h-0 px-0 md:px-8 py-2 md:py-6">
          <div className="relative flex flex-col items-center justify-center gap-1 py-2 px-4 border-b border-border/20">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center shadow-lg">
              <Crown className="w-6 h-6 text-white" />
            </div>
            <div className="flex items-center gap-2">
                <h3 className="font-bold text-lg text-foreground">FinSight AI</h3>
                <Badge className="bg-amber-500 text-white border-amber-600 text-xs">PRO</Badge>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-500 font-medium">Online</span>
            </div>
          </div>

          {/* Chat Messages Display Area */}
          <div className="flex-1 flex flex-col min-h-0">
            <div
              className="flex-1 flex flex-col gap-1 px-2 md:px-6 py-1 overflow-y-auto w-full min-h-[50px]"
              tabIndex={0}
              aria-label="Chat messages area"
              ref={chatScrollRef}
              style={{scrollBehavior: 'smooth'}}
              onScroll={handleChatScroll}
            >
              <div className="w-full">
                {messages.length === 0 && !isTyping ? (
                    <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                      <MessageSquare className="w-12 h-12 mb-4 text-amber-500/50" />
                      <p className="text-lg font-semibold">Start a Pro Conversation</p>
                      <p className="text-sm">Ask for advanced analytics or real-time data.</p>
                    </div>
                ) : (
                    messages.map((message, idx) => (
                      <div
                        key={message.id}
                        className={`flex ${message.type === "user" ? "justify-end" : "justify-start"} items-end animate-fade-in mb-1 group`}
                        style={{ animationDelay: `${idx * 0.05}s` }}
                        tabIndex={0}
                        aria-label={message.type === "user" ? "Your message" : "AI message"}
                      >
                        {message.type === "ai" && (
                          <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center mr-2 flex-shrink-0 shadow-md">
                            <Bot className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div
                          className={`rounded-2xl px-4 py-2 text-sm shadow-lg break-words relative transition-all duration-200 ${
                            message.type === "ai"
                              ? "bg-gradient-to-br from-background/90 to-zinc-800/20 text-foreground border border-border/30"
                              : "bg-primary text-primary-foreground"
                          }`}
                          style={{ width: 'fit-content', maxWidth: '90%' }}
                        >
                          {message.content}
                          <span className="block text-[10px] text-muted-foreground mt-1 text-right opacity-80 select-none">
                            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          {message.type === "ai" && message.suggestions && message.suggestions.length > 0 && (
                            <div className="flex flex-wrap gap-2 mt-2 pt-2 border-t border-border/50">
                              {message.suggestions.map((suggestion, sIdx) => (
                                <Badge
                                  key={sIdx}
                                  variant="secondary"
                                  className="cursor-pointer hover:bg-amber-400/20 hover:text-amber-300 transition-colors text-xs py-1 px-2 rounded-full"
                                  onClick={() => handleSuggestionClick(suggestion)}
                                >
                                  {suggestion}
                                </Badge>
                              ))}
                            </div>
                          )}
                          {message.type === "ai" && message.showChart && (
                            <div className="mt-4 border-t border-border/50 pt-3">
                              <ChartContainer
                                config={{}}
                                className="aspect-auto h-[250px] w-full"
                              >
                                <div className="flex items-center justify-center h-full border border-dashed border-amber-500/50 rounded-lg bg-background/50 text-amber-400">
                                  <BarChart2 className="w-8 h-8 mr-2" />
                                  <span>Pro Chart Placeholder (Real-time Data)</span>
                                </div>
                              </ChartContainer>
                            </div>
                          )}
                        </div>
                        {message.type === "user" && (
                          <div className="w-7 h-7 rounded-full bg-muted flex items-center justify-center ml-2 flex-shrink-0 shadow-md border-2 border-amber-500">
                            {user && user.photoURL ? (
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
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center flex-shrink-0 shadow-md">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="bg-background/90 border border-border/50 px-3 py-2 rounded-2xl flex items-center gap-1 shadow-md">
                      <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" />
                      <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                      <div className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Floating Input Bar (Pro) */}
            <div className="border-t border-border/20 bg-background/95 sticky bottom-0 z-10 shadow-2xl">
              <form
                className="flex items-center gap-3 w-full px-3 md:px-6 py-3 rounded-xl bg-background/95 shadow-lg mt-2"
                onSubmit={e => {
                  e.preventDefault();
                  handleSendMessage(inputValue);
                }}
                aria-label="Send a message"
              >
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  placeholder="Ask FinSight AI anything..."
                  className="flex-1 min-h-[44px] pr-12 text-base shadow-sm focus-visible:ring-offset-0 focus-visible:ring-amber-500/50"
                  disabled={isInputDisabled}
                  autoFocus
                />
                <Button
                  type="submit"
                  size="icon"
                  className="w-10 h-10 rounded-full bg-amber-500 hover:bg-amber-600 absolute right-6 md:right-9"
                  disabled={isInputDisabled}
                >
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