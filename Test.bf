using System;
using System.IO;

namespace Test
{
    // <summary>
    // Just a test class
    // </summary>
    public class TestClass
    {
        // <summary>
        // Just a test class inside a test class
        // </summary>
        public class TestClassInsideTestClass
        {

        }

        // <summary>
        // Just a test method
        // </summary>
        public void PublicMethod() {}
        
        // <summary>
        // Just a private test method
        // </summary>
        private void PrivateMethod() {}

        // <summary>
        // Just a unspecified test method
        // </summary>
        void UnspecifiedMethod() {}
    }

    // <summary>
    // Just a private test class
    // </summary>
    private class PrivateTestClass
    {

    }

    // <summary>
    // Just a unspecified test class
    // </summary>
    class UnspecifiedTestClass
    {

    }
}

namespace Test.Sub
{
    // <summary>
    // Just another test class
    // </summary>
    public class SubTestClass
    {

    }
}